from __future__ import annotations

import atexit
import random
import asyncio
import logging
import threading
from typing import TYPE_CHECKING, Any, List, Mapping, Callable, Iterator, Optional, AsyncIterator

from ._state import (
    BufferPool,
    FailureKind,
    BackoffPolicy,
    RecoveryState,
    iter_frames,
    classify_fatal_error,
    classify_handshake_status,
)
from ._types import (
    DEFAULT_AUDIO_FORMAT,
    BufferGap,
    Reconnected,
    Reconnecting,
    BufferOptions,
    SessionStarted,
    TranscriptDelta,
    ReconnectOptions,
    TranscriptFailed,
    EchoResponseEvent,
    TurnDetectionParam,
    SessionCreatedEvent,
    TranscriptCompleted,
    RealtimeSessionEvent,
    TranscriptionDeltaEvent,
    TranscriptionFailedEvent,
    TranscriptionCompletedEvent,
    InputAudioBufferProcessedEvent,
    echo_event,
    clear_event,
    append_event,
    commit_event,
    sample_rate_of,
    session_update_event,
)
from ._connection import (
    AsyncRealtimeConnection,
    AsyncRealtimeConnectionManager,
    _session_config,
    handshake_status_of,
)
from ._exceptions import (
    RealtimeError,
    RealtimeSessionError,
    RealtimeConnectionError,
    RealtimeIdleTimeoutError,
    RealtimeInvalidStateError,
)

if TYPE_CHECKING:
    from ..._client import AsyncTogether

__all__ = [
    "AsyncRealtimeTranscriptionSession",
    "RealtimeTranscriptionSession",
    "DEFAULT_RECONNECT_THROTTLE",
]

log = logging.getLogger("together.realtime")

_SENTINEL = object()

# Caps concurrent reconnect handshakes process-wide so a shared network blip
# with thousands of sessions doesn't stampede the server.
DEFAULT_RECONNECT_THROTTLE = threading.BoundedSemaphore(32)

_DEFAULT_POOL = BufferPool()

# Internal liveness cadence: probe every ~5s (jittered), declare the path dead
# if a probe goes unanswered for 2s, and force-reconnect if audio is flowing
# but no server events arrive for 30s.
_ECHO_INTERVAL = 5.0
_ECHO_TIMEOUT = 2.0
_STALE_STREAM_TIMEOUT = 30.0

# WebSocket close code (application-private range) the server pairs with the
# no_healthy_workers failed frame: this endpoint cannot serve, fail over to
# another one. The close is the primary signal; the JSON frame is informational.
RETRY_ELSEWHERE_CLOSE_CODE = 4503


class AsyncRealtimeTranscriptionSession:
    """Auto-reconnecting realtime transcription session (async).

    Maintains an SDK-side recovery buffer; on retryable failures it reconnects
    with backoff and replays un-acknowledged audio from the last transcribed
    position (the `completed` event's start + duration, minus a safety margin).
    Iterate the session to consume normalized events.
    """

    def __init__(
        self,
        *,
        client: AsyncTogether,
        model: str,
        input_audio_format: str = DEFAULT_AUDIO_FORMAT,
        sample_rate: Optional[int] = None,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        rolling_prompt: Optional[bool] = None,
        energy_gate_rms: Optional[float] = None,
        session_params: Optional[Mapping[str, Any]] = None,
        turn_detection: Optional[TurnDetectionParam] = None,
        reconnect: Optional[ReconnectOptions] = None,
        buffer: Optional[BufferOptions] = None,
        keepalive_silence: bool = False,
        reprime_prompt: bool = False,
        max_chunk_ms: float = 1000.0,
        pool: Optional[BufferPool] = None,
        event_callback: Optional[Callable[[RealtimeSessionEvent], None]] = None,
        extra_query: Optional[Mapping[str, Any]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        reconnect_throttle: Optional[threading.BoundedSemaphore] = None,
    ) -> None:
        expected_rate = sample_rate_of(input_audio_format)
        if sample_rate is not None and sample_rate != expected_rate:
            raise ValueError(
                f"audio source is {sample_rate}Hz but input_audio_format={input_audio_format!r} "
                f"expects {expected_rate}Hz — resample before appending"
            )
        self._manual_commit = turn_detection is not None and turn_detection.get("type") == "none"
        if keepalive_silence and not self._manual_commit:
            raise ValueError(
                "keepalive_silence requires turn_detection={'type': 'none'}: with server VAD "
                "enabled, injected silence would finalize a user utterance at a natural pause"
            )

        reconnect = reconnect or {}
        buffer = buffer or {}

        self._client = client
        self._model = model
        self._format = input_audio_format
        self._language = language
        self._prompt = prompt
        self._rolling_prompt = rolling_prompt
        self._energy_gate_rms = energy_gate_rms
        self._session_params = session_params
        self._turn_detection = turn_detection
        self._extra_query = extra_query
        self._extra_headers = extra_headers
        self._keepalive_silence = keepalive_silence
        self._reprime_prompt = reprime_prompt
        self._event_callback = event_callback
        self._throttle = reconnect_throttle or DEFAULT_RECONNECT_THROTTLE

        self._backoff = BackoffPolicy(
            initial=reconnect.get("backoff_initial", 0.5),
            maximum=reconnect.get("backoff_max", 15.0),
            max_attempts=reconnect.get("max_attempts", 2),
            max_elapsed=reconnect.get("max_elapsed", 120.0),
        )
        pool = pool if pool is not None else _DEFAULT_POOL
        self.state = RecoveryState(
            input_audio_format=input_audio_format,
            replay_margin=buffer.get("replay_margin", 0.0),
            max_replay_seconds=buffer.get("max_replay_seconds", 5.0),
            max_seconds=buffer.get("max_seconds", 120.0),
            overflow=buffer.get("overflow", "drop_oldest"),
            pool=pool,
        )
        # registered with the pool in start(), not here: the pool holds a
        # strong reference (via the held_bytes closure) until close()/_fail(),
        # so a session that is constructed but never started must not be
        # pinned by the client-scoped pool forever
        self._pool = pool

        # Liveness probing is internal (not part of the public API): a small
        # application-level ping catches silent failures — connection looks
        # open but the server stopped responding — within a few seconds.
        self._echo_interval = _ECHO_INTERVAL
        self._echo_timeout = _ECHO_TIMEOUT
        self._stale_stream_timeout = _STALE_STREAM_TIMEOUT

        # audio passes through with the caller's own chunk boundaries; this
        # cap only splits oversized chunks so one websocket message never
        # exceeds what the server will parse
        self._max_chunk_bytes = max(2, int(self.state.bps * max_chunk_ms / 1000.0))
        self._events: asyncio.Queue[Any] = asyncio.Queue()
        self._connection: Optional[AsyncRealtimeConnection] = None
        self._reader_task: Optional[asyncio.Task[None]] = None
        self._watchdog_task: Optional[asyncio.Task[None]] = None
        self._reconnect_task: Optional[asyncio.Task[None]] = None
        self._writer_task: Optional[asyncio.Task[None]] = None
        self._writer_wakeup = asyncio.Event()
        self._sent_offset = 0
        # control events (e.g. commit) ordered by buffer offset: sent by the
        # writer only once all audio before the offset has been sent
        self._pending_controls: List[Any] = []  # list[tuple[int, dict]]
        self._replaying_until = 0

        self._closed = False
        self._failure: Optional[BaseException] = None
        self._echo_pending_since: Optional[float] = None
        self._last_server_event = 0.0
        self._last_transcript_event = 0.0
        self._last_append_at = 0.0
        self._connected_at = 0.0
        self.transcripts: List[str] = []
        self._warned_riff = False
        self._warned_silence = False

    # -- lifecycle ---------------------------------------------------------

    async def __aenter__(self) -> "AsyncRealtimeTranscriptionSession":
        await self.start()
        return self

    async def __aexit__(self, exc_type: object, *_exc: object) -> None:
        if exc_type is None and self._failure is None and not self._closed:
            try:
                await self.flush()
            except RealtimeError:
                pass
        await self.close()

    async def start(self) -> None:
        if self._connection is not None:
            return
        try:
            connection = await self._open_connection()
        except Exception as exc:
            status = handshake_status_of(exc)
            detail = f"HTTP {status}" if status is not None else exc.__class__.__name__
            raise RealtimeConnectionError(
                f"could not open realtime connection to {self._client.base_url} ({detail}); "
                "check that base_url / TOGETHER_BASE_URL points at an API root that "
                "serves /realtime, e.g. https://api.together.ai/v1",
                cause=exc,
            ) from exc
        try:
            created = await self._await_session_created(connection)
        except BaseException:
            await _close_quietly(connection)
            raise
        self.state.begin_epoch(self.state.write_head)
        self._sent_offset = self.state.write_head
        self._pool.register(self, lambda: self.state.buffer.size, self.state.reclaim)
        self._attach(connection)
        self._emit(
            SessionStarted(
                session_id=created.session.id if created.session else None,
                model=self.model,
                epoch=self.state.epoch,
            )
        )
        self._writer_task = asyncio.create_task(self._writer_loop())
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    async def close(self) -> None:
        # No early-return on _closed: _fail() sets it without awaiting the
        # reader/reconnect tasks, so a close() after a terminal failure must
        # still run the (idempotent) teardown below to be deterministic.
        self._closed = True
        self._writer_wakeup.set()
        tasks = [
            task
            for task in (self._watchdog_task, self._writer_task, self._reconnect_task, self._reader_task)
            if task is not None
        ]
        for task in tasks:
            task.cancel()
        # await the cancellations so shutdown is deterministic: the sync facade
        # stops the loop right after close() returns, and a still-pending task
        # would be destroyed mid-teardown (asyncio warnings, half-closed socket)
        current = asyncio.current_task()
        pending = [task for task in tasks if task is not current]
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception:
                pass
            self._connection = None
        self._pool.unregister(self)
        self._events.put_nowait(_SENTINEL)

    # -- public API ----------------------------------------------------------

    async def append(self, pcm: bytes) -> None:
        """Buffer PCM audio for transmission. Never blocks on reconnection.

        If the session has failed terminally, raises that failure (e.g.
        RealtimeConnectionError) so a plain feed loop can drive failover
        without a separate consumer task watching for errors.
        """
        self._raise_if_failed()
        if self._closed:
            raise RealtimeInvalidStateError("append() after close()")
        self._sanity_check_audio(pcm)
        self.state.record_append(pcm)
        self._flush_gap_events()
        self._last_append_at = self._now()
        self._writer_wakeup.set()

    async def commit(self) -> None:
        """Finalize the buffered tail (required when turn_detection='none')."""
        self._raise_if_failed()
        if self._closed:
            raise RealtimeInvalidStateError("commit() after close()")
        self.state.record_commit()
        self._pending_controls.append((self.state.write_head, commit_event()))
        self._writer_wakeup.set()

    async def clear(self) -> None:
        """Drop buffered audio on the server and in the SDK recovery buffer."""
        self._raise_if_failed()
        if self._closed:
            raise RealtimeInvalidStateError("clear() after close()")
        self.state.record_clear()
        self._pending_controls.clear()
        self._sent_offset = self.state.write_head
        if self._connection is not None:
            await self._connection.send(clear_event())

    async def flush(self, *, quiescence: float = 2.0, timeout: float = 30.0) -> str:
        """Commit the buffered tail and wait until transcript events go quiet.

        Commit works with server VAD too — it force-finalizes in-progress
        speech, so the tail utterance gets a final transcript. Bounded by
        `timeout`; uses event quiescence rather than any exact completeness
        signal (a commit can legitimately yield zero transcripts). Returns the
        concatenation of all final transcripts seen so far.
        """
        if self.state.write_head > (self.state.anchor or 0):
            await self.commit()
        self._raise_if_failed()
        started = self._now()
        deadline = started + timeout
        while self._now() < deadline:
            if self._failure is not None:
                raise self._failure
            if self._closed:
                break
            fully_sent = self._sent_offset >= self.state.write_head and not self._pending_controls
            # the quiescence clock starts at flush time so the commit sent
            # above always gets a response window: a final for the tail
            # utterance may land seconds after the last transcript event
            quiet_for = self._now() - max(self._last_transcript_event, self._connected_at, started)
            if fully_sent and quiet_for >= quiescence and self._reconnect_task is None:
                break
            await asyncio.sleep(min(0.1, quiescence / 4))
        return " ".join(self.transcripts)

    def pending_audio(self) -> bytes:
        """Audio appended but not yet covered by a final transcript.

        The recovery primitive for orchestrating failover OUTSIDE the SDK:
        when this session fails terminally (RealtimeConnectionError after
        retries), feed this audio — together with a prompt built from
        `self.transcripts` — into a fresh session on an alternate endpoint to
        resume where this one left off.
        """
        plan = self.state.replay_plan()
        return b"".join(self.state.buffer.read_from(plan.start_offset))

    def context_prompt(self, max_chars: int = 200) -> str:
        """Tail of the delivered transcripts, suitable as `prompt` for a
        successor session (mirrors the server's rolling-prompt context)."""
        return " ".join(self.transcripts)[-max_chars:]

    def _raise_if_failed(self) -> None:
        if self._failure is not None:
            raise self._failure

    async def drain(self) -> str:
        """Alias for flush() then close(); returns the final transcript."""
        text = await self.flush()
        await self.close()
        return text

    @property
    def metrics(self) -> Any:
        return self.state.metrics

    def __aiter__(self) -> AsyncIterator[RealtimeSessionEvent]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[RealtimeSessionEvent]:
        while True:
            item = await self._events.get()
            if item is _SENTINEL:
                break
            yield item
        if self._failure is not None:
            raise self._failure

    # -- internals: connection ------------------------------------------------

    @property
    def model(self) -> str:
        return self._model

    def _manager(self) -> AsyncRealtimeConnectionManager:
        # language goes to the manager (it lands on the connection URL, the
        # only place the server honors it — together-py#505); the manager is
        # rebuilt per _open_connection() call, so reconnects keep it too
        return AsyncRealtimeConnectionManager(
            client=self._client,
            model=self.model,
            input_audio_format=self._format,
            turn_detection=self._turn_detection,
            language=self._language,
            extra_query=self._extra_query,
            extra_headers=self._extra_headers,
        )

    async def _open_connection(self) -> AsyncRealtimeConnection:
        return await self._manager().connect()

    async def _await_session_created(self, connection: AsyncRealtimeConnection) -> SessionCreatedEvent:
        try:
            event = await asyncio.wait_for(connection.recv(), timeout=10.0)
        except asyncio.TimeoutError:
            raise RealtimeConnectionError("timed out waiting for session.created") from None
        except Exception as exc:
            # An endpoint that is unhealthy AT CONNECT TIME closes before ever
            # sending session.created; without this, the raw websockets error
            # would leak out of start() and a failover loop keyed on
            # RealtimeConnectionError (and .code) would miss it.
            if connection.close_code == RETRY_ELSEWHERE_CLOSE_CODE:
                raise RealtimeConnectionError(
                    "endpoint signaled no healthy workers; failing over",
                    code="no_healthy_workers",
                    cause=exc,
                ) from exc
            raise RealtimeConnectionError(
                f"connection closed before session.created ({exc.__class__.__name__})", cause=exc
            ) from exc
        if not isinstance(event, SessionCreatedEvent):
            raise RealtimeConnectionError(f"expected session.created, got {getattr(event, 'type', event)!r}")
        await self._configure_session(connection)
        return event

    async def _configure_session(self, connection: AsyncRealtimeConnection) -> None:
        # single source of truth for the session-param field mapping lives in
        # _connection._session_config; only the reprime tail is layered on here.
        # language is set at the beginning of the session on the connection
        # URL (see _manager / build_realtime_url)
        session = _session_config(
            prompt=self._effective_prompt(),
            rolling_prompt=self._rolling_prompt,
            energy_gate_rms=self._energy_gate_rms,
            session_params=self._session_params,
        )
        if session:
            await connection.send(session_update_event(session))

    def _effective_prompt(self) -> Optional[str]:
        prompt = self._prompt
        if self._reprime_prompt and self.transcripts:
            # restore the decode context the server lost with the old connection
            tail = " ".join(self.transcripts)[-200:]
            prompt = f"{prompt} {tail}".strip() if prompt else tail
        return prompt

    def _attach(self, connection: AsyncRealtimeConnection) -> None:
        self._connection = connection
        self._connected_at = self._now()
        self._echo_pending_since = None
        self._last_server_event = self._now()
        epoch = self.state.epoch
        self._reader_task = asyncio.create_task(self._reader_loop(connection, epoch))

    # -- internals: reader ------------------------------------------------------

    async def _reader_loop(self, connection: AsyncRealtimeConnection, epoch: int) -> None:
        try:
            while True:
                try:
                    event = await asyncio.wait_for(connection.recv(), timeout=0.5)
                except asyncio.TimeoutError:
                    # A graceful server close can stall for the server's
                    # close_timeout while we're bursting appends; don't wait
                    # the handshake out — reconnect as soon as CLOSING shows.
                    if connection.is_closing():
                        raise ConnectionError("server initiated close") from None
                    continue
                if self._closed:
                    return
                if self.state.epoch != epoch:
                    return  # stale connection still draining; drop its events
                self._handle_server_event(event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if self._closed or self.state.epoch != epoch:
                return
            # The server signals "fail over to another endpoint" with a WS close
            # code; retrying this endpoint is futile, so fail terminally instead
            # of reconnecting. Other closes are treated as recoverable drops.
            if connection.close_code == RETRY_ELSEWHERE_CLOSE_CODE:
                self._fail(
                    RealtimeConnectionError(
                        "endpoint signaled no healthy workers; failing over",
                        code="no_healthy_workers",
                    )
                )
                return
            self._schedule_reconnect(f"connection lost: {exc.__class__.__name__}")

    def _handle_server_event(self, event: object) -> None:
        now = self._now()
        self._last_server_event = now

        if isinstance(event, TranscriptionDeltaEvent):
            self._last_transcript_event = now
            seg = self.state.segment_for(event.item_id, replayed=self._is_replayed_now())
            self.state.metrics.delta_events += 1
            self._emit(
                TranscriptDelta(
                    segment_id=seg.segment_id,
                    text=event.delta,
                    audio_start=seg.audio_start,
                    audio_end=self.state.to_seconds(self.state.write_head),
                    replayed=seg.replayed,
                    logprobs=event.logprobs,
                    tokens=event.tokens,
                    raw=event,
                )
            )
        elif isinstance(event, TranscriptionCompletedEvent):
            self._last_transcript_event = now
            seg = self.state.segment_for(event.item_id, replayed=self._is_replayed_now())
            processed_seconds = (
                event.start + event.duration if event.start is not None and event.duration is not None else None
            )
            self.state.record_completed(processed_seconds)
            self.state.close_segment(event.item_id)
            if event.transcript:
                self.transcripts.append(event.transcript)
            self._emit(
                TranscriptCompleted(
                    segment_id=seg.segment_id,
                    text=event.transcript,
                    audio_start=seg.audio_start,
                    audio_end=self.state.to_seconds(self.state.anchor or self.state.write_head),
                    replayed=seg.replayed,
                    logprobs=event.logprobs,
                    tokens=event.tokens,
                    raw=event,
                )
            )
            self._flush_gap_events()
        elif isinstance(event, TranscriptionFailedEvent):
            if event.is_fatal:
                self._handle_fatal_failed(event)
            else:
                seg = self.state.segment_for(event.item_id, replayed=False)
                self.state.close_segment(event.item_id)
                self._emit(
                    TranscriptFailed(
                        segment_id=seg.segment_id,
                        message=event.error.message if event.error else None,
                        raw=event,
                    )
                )
        elif isinstance(event, InputAudioBufferProcessedEvent):
            self.state.record_processed(event.processed_ms)
        elif isinstance(event, EchoResponseEvent):
            self._echo_pending_since = None
        # turn events / unknown events are intentionally not surfaced by the
        # normalized stream; use client.beta.realtime.connect() for raw access.

    def _is_replayed_now(self) -> bool:
        """Events for audio at or before the replay watermark came from replayed bytes."""
        return self.state.write_head <= self._replaying_until

    def _handle_fatal_failed(self, event: TranscriptionFailedEvent) -> None:
        kind = classify_fatal_error(event.error)
        message = (event.error.message if event.error else None) or "realtime session failed"
        if kind is FailureKind.RETRYABLE:
            self._schedule_reconnect(message)
        elif kind is FailureKind.RETRY_ELSEWHERE:
            # Informational only: the server closes with RETRY_ELSEWHERE_CLOSE_CODE
            # right after this frame, and that close is what drives failover (see
            # _reader_loop). Don't reconnect here (futile) and don't fail yet.
            return
        elif kind is FailureKind.IDLE_TIMEOUT:
            plan = self.state.replay_plan()
            if plan.start_offset < self.state.write_head or plan.resend_commit:
                self._schedule_reconnect("idle timeout with unreplayed audio")
            else:
                self._fail(
                    RealtimeIdleTimeoutError(
                        "server closed the session after 300s without audio appends; "
                        "enable keepalive_silence or append audio continuously"
                    )
                )
        else:
            self._fail(
                RealtimeSessionError(
                    message,
                    error_type=event.error.type if event.error else None,
                    code=event.error.code if event.error else None,
                    raw=event,
                )
            )

    # -- internals: writer -------------------------------------------------------

    async def _writer_loop(self) -> None:
        """Drain the buffer cursor to the current connection.

        Replay and live streaming are the same code path: reconnect simply
        moves `_sent_offset` back to the replay start.
        """
        try:
            while not self._closed:
                # clear before checking for work so an append landing mid-drain
                # re-sets it and the wait below returns immediately
                self._writer_wakeup.clear()
                connection = self._connection
                progressed = False
                if connection is not None and self._reconnect_task is None:
                    while self._sent_offset < self.state.write_head:
                        # chunk boundaries are the caller's own append() chunks
                        # (the buffer stores them as appended); a chunk is only
                        # split when it exceeds the per-message safety cap
                        chunks = list(self.state.buffer.read_from(self._sent_offset))
                        if not chunks:
                            # cursor points below retained data (trimmed); skip ahead
                            self._sent_offset = max(self._sent_offset, self.state.buffer.start_offset)
                            if self._sent_offset >= self.state.write_head:
                                break
                            continue
                        for chunk in chunks:
                            for piece in iter_frames(chunk, self._max_chunk_bytes):
                                await connection.send(append_event(piece))
                                self._sent_offset += len(piece)
                                await self._maybe_send_controls(connection)
                        progressed = True
                    await self._maybe_send_controls(connection)
                if not progressed:
                    # No progress possible right now (nothing to send, no
                    # connection, or a reconnect is in flight). ALWAYS yield
                    # here: unsent audio accumulating during a reconnect must
                    # not turn this loop into a busy-spin that starves the
                    # event loop (and with it the reconnect task itself).
                    try:
                        await asyncio.wait_for(self._writer_wakeup.wait(), timeout=0.25)
                    except asyncio.TimeoutError:
                        pass
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if not self._closed:
                self._schedule_reconnect(f"send failed: {exc.__class__.__name__}")
                # writer restarts with the new connection
                self._writer_task = asyncio.create_task(self._writer_loop())

    async def _maybe_send_controls(self, connection: AsyncRealtimeConnection) -> None:
        while self._pending_controls and self._pending_controls[0][0] <= self._sent_offset:
            _offset, control = self._pending_controls.pop(0)
            await connection.send(control)

    # -- internals: reconnect ------------------------------------------------------

    def _schedule_reconnect(self, reason: str) -> None:
        if self._closed or self._failure is not None:
            return
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return  # single-flight
        self._reconnect_task = asyncio.create_task(self._reconnect(reason))

    async def _reconnect(self, reason: str) -> None:
        old_connection = self._connection
        started = self._now()
        attempt = 0
        try:
            while not self._closed:
                self._emit(Reconnecting(attempt=attempt + 1, reason=reason, model=self.model))
                delay = self._backoff.delay(attempt)
                if delay:
                    await asyncio.sleep(delay)
                attempt += 1
                if attempt > self._backoff.max_attempts or (self._now() - started) > self._backoff.max_elapsed:
                    self._fail(
                        RealtimeConnectionError(
                            f"reconnect failed after {attempt - 1} attempts ({reason})",
                            attempts=attempt - 1,
                        )
                    )
                    return
                try:
                    await self._acquire_throttle()
                    try:
                        connection = await self._open_connection()
                        try:
                            created = await self._await_session_created(connection)
                        except BaseException:
                            await _close_quietly(connection)
                            raise
                    finally:
                        self._throttle.release()
                except Exception as exc:
                    # A 4503 close before session.created means this endpoint
                    # cannot serve; retrying it is futile — fail over now
                    # instead of burning the remaining reconnect budget.
                    if isinstance(exc, RealtimeConnectionError) and exc.code == "no_healthy_workers":
                        self._fail(
                            RealtimeConnectionError(
                                "endpoint signaled no healthy workers; failing over",
                                attempts=attempt,
                                code="no_healthy_workers",
                                cause=exc,
                            )
                        )
                        return
                    status = handshake_status_of(exc)
                    kind = classify_handshake_status(status) if status is not None else FailureKind.RETRYABLE
                    if kind is FailureKind.FATAL_AUTH or kind is FailureKind.FATAL:
                        self._fail(
                            RealtimeConnectionError(
                                f"reconnect rejected with HTTP {status}", attempts=attempt, cause=exc
                            )
                        )
                        return
                    reason = f"handshake failed: {exc.__class__.__name__}"
                    continue

                # make-before-break: the new connection is live before the old
                # socket is torn down; the epoch bump quarantines stale frames.
                plan = self.state.replay_plan()
                gap = self.state.consume_pending_gap()
                if plan.gap_bytes or gap:
                    self._emit(
                        BufferGap(
                            dropped_seconds=self.state.to_seconds(plan.gap_bytes + gap),
                            reason="replay window capped",
                        )
                    )
                self.state.begin_epoch(plan.start_offset)
                self._sent_offset = plan.start_offset
                self._replaying_until = self.state.write_head
                self.state.metrics.replayed_bytes += max(0, self.state.write_head - plan.start_offset)
                if plan.resend_commit and self.state.outstanding_commits:
                    boundary = max(self.state.outstanding_commits)
                    self._pending_controls = [(boundary, commit_event())]
                self._attach(connection)
                if old_connection is not None:
                    try:
                        await old_connection.close()
                    except Exception:
                        pass
                self._emit(
                    Reconnected(
                        attempt=attempt,
                        replayed_seconds=self.state.to_seconds(self.state.write_head - plan.start_offset),
                        model=self.model,
                    )
                )
                self._writer_wakeup.set()
                _created = created  # session id available if callers need it later
                return
        except asyncio.CancelledError:
            raise
        finally:
            self._reconnect_task = None

    async def _acquire_throttle(self) -> None:
        while not self._throttle.acquire(blocking=False):
            await asyncio.sleep(0.05 + random.random() * 0.1)

    # -- internals: watchdog -------------------------------------------------------

    async def _watchdog_loop(self) -> None:
        next_echo = self._now() + self._jittered(self._echo_interval)
        while not self._closed:
            await asyncio.sleep(0.5)
            try:
                now = self._now()
                connection = self._connection
                if connection is None or self._reconnect_task is not None:
                    continue

                # echo liveness probe: a live heartbeat means the server path is
                # healthy; a missed one means it isn't — reconnect proactively
                # (make-before-break) instead of waiting for TCP to notice.
                if self._echo_pending_since is not None:
                    if now - self._echo_pending_since > self._echo_timeout:
                        self._echo_pending_since = None
                        self._schedule_reconnect("echo timeout")
                        # reconnect in flight: stale-stream/keepalive checks below
                        # are intentionally skipped this tick
                        continue
                elif now >= next_echo:
                    next_echo = now + self._jittered(self._echo_interval)
                    self._echo_pending_since = now
                    try:
                        await connection.send(echo_event(echo_id=int(now * 1000)))
                    except Exception:
                        self._schedule_reconnect("echo send failed")
                        continue

                # stale stream: audio flowing, echo answering, but zero events —
                # the decode path is wedged
                audio_in_flight = self._sent_offset > 0 and self._last_append_at > self._last_server_event
                if (
                    audio_in_flight
                    and now - max(self._last_server_event, self._connected_at) > self._stale_stream_timeout
                ):
                    self._schedule_reconnect("stale stream (audio flowing, no server events)")
                    continue  # skip keepalive this tick; reconnect owns the connection now

                # keepalive silence (manual-commit mode only): defeat the server's
                # 300s no-append idle timeout
                if self._keepalive_silence and self._last_append_at:
                    if now - self._last_append_at > 200.0:
                        await self.append(b"\x00" * int(self.state.bps * 0.1))  # 100ms of silence
            except asyncio.CancelledError:
                raise
            except Exception:
                # the keepalive append can raise (overflow='error', or a stored
                # terminal failure via _raise_if_failed); the watchdog must
                # survive it — dying here silently loses echo probing and
                # keepalive while the session still looks healthy
                if self._closed or self._failure is not None:
                    return
                log.exception("realtime watchdog iteration failed; liveness probing continues")

    def _jittered(self, interval: float) -> float:
        return interval * (0.8 + 0.4 * random.random())

    # -- internals: misc --------------------------------------------------------

    def _now(self) -> float:
        return asyncio.get_running_loop().time()

    def _emit(self, event: RealtimeSessionEvent) -> None:
        if self._event_callback is not None:
            try:
                self._event_callback(event)
            except Exception:
                log.exception("realtime event callback raised")
        else:
            self._events.put_nowait(event)

    def _fail(self, error: BaseException) -> None:
        if self._failure is None:
            self._failure = error
        self._closed = True
        self._events.put_nowait(_SENTINEL)
        for task in (self._watchdog_task, self._writer_task):
            if task is not None:
                task.cancel()
        if self._connection is not None:
            connection = self._connection
            self._connection = None
            asyncio.ensure_future(_close_quietly(connection))
        self._pool.unregister(self)

    def _flush_gap_events(self) -> None:
        gap = self.state.consume_pending_gap()
        if gap:
            self._emit(BufferGap(dropped_seconds=self.state.to_seconds(gap), reason="recovery buffer overflow"))

    def _sanity_check_audio(self, pcm: bytes) -> None:
        if not self._warned_riff and pcm[:4] == b"RIFF":
            self._warned_riff = True
            log.warning(
                "append() received what looks like a WAV file (RIFF header); "
                "the realtime API expects raw PCM frames — strip the WAV header first"
            )
        if not self._warned_silence and len(pcm) >= self.state.bps and pcm.count(0) == len(pcm):
            self._warned_silence = True
            log.warning("append() has received >=1s of all-zero audio — is the microphone live?")


async def _close_quietly(connection: AsyncRealtimeConnection) -> None:
    try:
        await connection.close()
    except Exception:
        pass


class RealtimeTranscriptionSession:
    """Sync facade over AsyncRealtimeTranscriptionSession.

    Runs the async session on a dedicated background event loop thread — one
    thread per session, so this surface is intended for low session counts;
    use the async client for high-concurrency deployments.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, name="together-realtime", daemon=True)
        self._thread.start()
        self._kwargs = kwargs
        self._session: Optional[AsyncRealtimeTranscriptionSession] = None
        atexit.register(self.close)

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_forever()
        finally:
            # close on the loop's own thread once run_forever returns: a
            # merely-stopped loop leaks its selector and self-pipe fds until
            # GC (ResourceWarning noise, fd exhaustion across many sessions)
            self._loop.close()

    def _call(self, coro: Any, timeout: Optional[float] = None) -> Any:
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout)

    def start(self) -> None:
        async def _create() -> AsyncRealtimeTranscriptionSession:
            session = AsyncRealtimeTranscriptionSession(**self._kwargs)
            try:
                await session.start()
            except BaseException:
                await session.close()
                raise
            return session

        try:
            self._session = self._call(_create())
        except BaseException:
            # a failed start (bad base_url, rejected handshake, bad kwargs)
            # must not strand the background loop thread until atexit
            self.close()
            raise

    def __enter__(self) -> "RealtimeTranscriptionSession":
        self.start()
        return self

    def __exit__(self, exc_type: object, *_exc: object) -> None:
        if self._session is not None and exc_type is None:
            try:
                self.flush()
            except RealtimeError:
                pass
        self.close()

    def append(self, pcm: bytes) -> None:
        assert self._session is not None, "session not started"
        self._call(self._session.append(pcm))

    def commit(self) -> None:
        assert self._session is not None, "session not started"
        self._call(self._session.commit())

    def clear(self) -> None:
        assert self._session is not None, "session not started"
        self._call(self._session.clear())

    def flush(self, *, quiescence: float = 2.0, timeout: float = 30.0) -> str:
        assert self._session is not None, "session not started"
        result = self._call(self._session.flush(quiescence=quiescence, timeout=timeout), timeout=timeout + 5)
        return str(result)

    @property
    def metrics(self) -> Any:
        assert self._session is not None, "session not started"
        return self._session.metrics

    def pending_audio(self) -> bytes:
        assert self._session is not None, "session not started"
        return self._session.pending_audio()

    def context_prompt(self, max_chars: int = 200) -> str:
        assert self._session is not None, "session not started"
        return self._session.context_prompt(max_chars)

    @property
    def transcripts(self) -> List[str]:
        assert self._session is not None, "session not started"
        return self._session.transcripts

    def __iter__(self) -> Iterator[RealtimeSessionEvent]:
        assert self._session is not None, "session not started"
        session = self._session
        while True:
            try:
                item = self._call(session._events.get())
            except Exception:
                return
            if item is _SENTINEL:
                if session._failure is not None:
                    raise session._failure
                return
            yield item

    def close(self) -> None:
        atexit.unregister(self.close)
        if self._session is not None:
            try:
                self._call(self._session.close(), timeout=10)
            except Exception:
                pass
            self._session = None
        try:
            # not gated on is_running(): scheduling stop before run_forever
            # has begun still stops the loop the moment it starts, closing
            # the construct-then-close race
            self._loop.call_soon_threadsafe(self._loop.stop)
        except RuntimeError:
            pass  # loop already stopped and closed
        if self._thread.is_alive():
            self._thread.join(timeout=5)
