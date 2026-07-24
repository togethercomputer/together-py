"""Failure-injection tests for the robust realtime transcription session.

Runs an in-process websockets server whose per-connection behavior is
scripted, so reconnect/replay behavior is exercised against real sockets.
Servers are created inside each test (not fixtures) to avoid event-loop
leakage across tests.
"""

from __future__ import annotations

import json
import base64
import socket
import asyncio
import logging
import contextlib
from typing import Any, Dict, List, Callable, Optional

import pytest

from together import AsyncTogether
from together.lib.realtime import (
    BufferGap,
    Reconnected,
    Reconnecting,
    SessionStarted,
    TranscriptDelta,
    TranscriptCompleted,
    RealtimeSessionError,
    RealtimeSessionEvent,
    RealtimeConnectionError,
)
from together.lib.realtime._state import BufferPool
from together.lib.realtime._session import (
    RealtimeTranscriptionSession,
    AsyncRealtimeTranscriptionSession,
)

BPS = 32_000  # pcm_s16le_16000


class ConnectionLog:
    """What one server-side connection observed."""

    def __init__(self) -> None:
        self.audio = bytearray()
        self.commits = 0
        self.events: List[Dict[str, Any]] = []
        self.path = ""


class FakeRealtimeServer:
    """Scriptable stand-in for the realtime transcription endpoint."""

    def __init__(
        self,
        *,
        reject_statuses: Optional[List[int]] = None,
        drop_after_bytes: Optional[int] = None,
        completed_every_bytes: Optional[int] = None,
        fatal_error: Optional[Dict[str, Any]] = None,
        close_code: Optional[int] = None,
        close_without_frame: bool = False,
        close_before_created_from: Optional[int] = None,
        complete_on_commit: bool = True,
        transcribed_fraction: float = 1.0,
        answer_echo: bool = True,
    ) -> None:
        self.reject_statuses = list(reject_statuses or [])
        self.drop_after_bytes = drop_after_bytes
        self.completed_every_bytes = completed_every_bytes
        self.fatal_error = fatal_error
        self.close_code = close_code
        self.close_without_frame = close_without_frame
        self.close_before_created_from = close_before_created_from
        """1-based connection index from which the server closes (with
        close_code) before ever sending session.created — an endpoint that is
        unhealthy at connect time."""
        self.complete_on_commit = complete_on_commit
        self.transcribed_fraction = transcribed_fraction
        self.answer_echo = answer_echo
        self.connections: List[ConnectionLog] = []
        self._server: Any = None

    async def __aenter__(self) -> "FakeRealtimeServer":
        from websockets.asyncio.server import serve

        self._server = await serve(self._handler, "127.0.0.1", 0, process_request=self._process_request)
        port = self._server.sockets[0].getsockname()[1]
        self.url = f"http://127.0.0.1:{port}"
        return self

    async def __aexit__(self, *_exc: object) -> None:
        self._server.close()
        await self._server.wait_closed()

    def _process_request(self, connection: Any, _request: Any) -> Any:
        if self.reject_statuses:
            status = self.reject_statuses.pop(0)
            return connection.respond(status, f"rejected {status}\n")
        return None

    async def _handler(self, ws: Any) -> None:
        conn = ConnectionLog()
        conn.path = getattr(ws.request, "path", "")
        self.connections.append(conn)
        item = len(self.connections) * 100
        if self.close_before_created_from is not None and len(self.connections) >= self.close_before_created_from:
            await ws.close(self.close_code or 1000, "unhealthy at connect")
            return
        await ws.send(
            json.dumps(
                {
                    "type": "session.created",
                    "event_id": "e1",
                    "session": {"id": f"s{len(self.connections)}", "object": "realtime.session"},
                }
            )
        )
        if self.close_without_frame and self.close_code is not None:
            # close code only, no JSON frame (e.g. frame lost, code survives)
            await ws.close(self.close_code, "no_healthy_workers")
            return
        if self.fatal_error is not None:
            await ws.send(
                json.dumps(
                    {
                        "type": "conversation.item.input_audio_transcription.failed",
                        "error": self.fatal_error,
                    }
                )
            )
            if self.close_code is not None:
                await ws.close(self.close_code, "no_healthy_workers")
            else:
                await ws.close()
            return
        emitted_at = 0
        try:
            async for message in ws:
                event = json.loads(message)
                conn.events.append(event)
                etype = event.get("type")
                if etype == "input_audio_buffer.append":
                    conn.audio.extend(base64.b64decode(event["audio"]))
                    if self.drop_after_bytes is not None and len(conn.audio) >= self.drop_after_bytes:
                        self.drop_after_bytes = None  # only the first connection drops
                        ws.transport.abort()  # simulate abrupt network failure
                        return
                    if (
                        self.completed_every_bytes is not None
                        and len(conn.audio) - emitted_at >= self.completed_every_bytes
                    ):
                        # like the real whisper handler, completed carries
                        # start/duration on the audio timeline
                        start_s = emitted_at / BPS
                        duration_s = (len(conn.audio) - emitted_at) / BPS * self.transcribed_fraction
                        emitted_at = len(conn.audio)
                        item += 1
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "conversation.item.input_audio_transcription.delta",
                                    "item_id": f"msg_{item}",
                                    "delta": f"partial-{item}",
                                }
                            )
                        )
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "conversation.item.input_audio_transcription.completed",
                                    "item_id": f"msg_{item}",
                                    "transcript": f"final-{item}",
                                    "start": start_s,
                                    "duration": duration_s,
                                }
                            )
                        )
                elif etype == "input_audio_buffer.commit":
                    conn.commits += 1
                    if self.complete_on_commit:
                        item += 1
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "conversation.item.input_audio_transcription.completed",
                                    "item_id": f"msg_{item}",
                                    "transcript": f"committed-{item}",
                                }
                            )
                        )
                elif etype == "echo" and self.answer_echo:
                    await ws.send(json.dumps({"type": "echo.response", "echo_id": event.get("echo_id")}))
        except Exception:
            pass


def make_session(server: FakeRealtimeServer, **overrides: Any) -> AsyncRealtimeTranscriptionSession:
    client = AsyncTogether(api_key="test-key", base_url=server.url)
    kwargs: Dict[str, Any] = dict(
        client=client,
        model="openai/whisper-large-v3",
        reconnect={"backoff_initial": 0.01, "backoff_max": 0.02, "max_attempts": 5, "max_elapsed": 5.0},
    )
    kwargs.update(overrides)
    return AsyncRealtimeTranscriptionSession(**kwargs)


async def collect_until(
    session: AsyncRealtimeTranscriptionSession,
    predicate: Callable[[List[RealtimeSessionEvent]], bool],
    timeout: float = 5.0,
) -> List[RealtimeSessionEvent]:
    """Consume session events until predicate(events) is truthy."""
    events: List[RealtimeSessionEvent] = []

    async def _consume() -> None:
        async for event in session:
            events.append(event)
            if predicate(events):
                return

    await asyncio.wait_for(_consume(), timeout)
    return events


def seconds(n: float) -> bytes:
    return b"\x01" * int(n * BPS)


class TestHappyPath:
    async def test_vad_flow_delta_completed(self) -> None:
        async with FakeRealtimeServer(completed_every_bytes=BPS) as server:
            session = make_session(server)
            async with session:
                await session.append(seconds(1.0))
                events = await collect_until(session, lambda evs: any(isinstance(e, TranscriptCompleted) for e in evs))
            assert isinstance(events[0], SessionStarted)
            deltas = [e for e in events if isinstance(e, TranscriptDelta)]
            finals = [e for e in events if isinstance(e, TranscriptCompleted)]
            assert deltas and finals
            assert finals[0].text.startswith("final-")
            assert finals[0].replayed is False
            assert server.connections[0].audio == seconds(1.0)

    async def test_manual_commit_flow(self) -> None:
        async with FakeRealtimeServer() as server:
            session = make_session(server, turn_detection={"type": "none"})
            async with session:
                await session.append(seconds(0.5))
                await session.commit()
                events = await collect_until(session, lambda evs: any(isinstance(e, TranscriptCompleted) for e in evs))
            finals = [e for e in events if isinstance(e, TranscriptCompleted)]
            assert finals[0].text.startswith("committed-")
            # commit was sent after all audio
            assert server.connections[0].commits == 1
            assert len(server.connections[0].audio) == len(seconds(0.5))


class TestSessionParams:
    async def test_session_level_params_sent_on_connect(self) -> None:
        async with FakeRealtimeServer() as server:
            session = make_session(
                server,
                language="en",
                prompt="medical terms",
                rolling_prompt=True,
                energy_gate_rms=0.02,
                session_params={"custom_engine_knob": "x"},
            )
            async with session:
                await session.append(seconds(0.1))
                await asyncio.sleep(0.1)
            updates = [e for e in server.connections[0].events if e["type"] == "transcription_session.updated"]
            assert updates, "expected a transcription_session.updated event"
            sent = updates[0]["session"]
            assert sent["language"] == "en"
            assert sent["prompt"] == "medical terms"
            assert sent["rolling_prompt"] is True
            assert sent["energy_gate_rms"] == 0.02
            assert sent["custom_engine_knob"] == "x"


class TestReconnect:
    async def test_drop_mid_stream_replays_from_anchor(self) -> None:
        async with FakeRealtimeServer(completed_every_bytes=BPS, drop_after_bytes=int(2.5 * BPS)) as server:
            session = make_session(server, buffer={"replay_margin": 1.0})
            async with session:
                await session.append(seconds(2.0))
                # wait for the completeds from the first connection (anchor advances)
                await collect_until(session, lambda evs: sum(isinstance(e, TranscriptCompleted) for e in evs) >= 2)
                await session.append(seconds(1.0))  # triggers the drop at 2.5s
                events = await collect_until(
                    session, lambda evs: any(isinstance(e, Reconnected) for e in evs), timeout=10.0
                )
                assert any(isinstance(e, Reconnecting) for e in events)
                assert len(server.connections) == 2
                # replay window = [anchor - margin, head]; anchor was at ~2s of
                # audio appended when the second completed arrived. Reconnected
                # fires before the writer drains, so wait for the replay bytes.
                replayed = await self._wait_bytes_stable(server, 1, int(1.0 * BPS))
                assert replayed <= int(2.0 * BPS)  # bounded: never the whole 3s buffer
                assert replayed >= int(1.0 * BPS)  # at least margin + post-anchor audio

    async def test_max_replay_seconds_zero_resumes_live(self) -> None:
        async with FakeRealtimeServer(drop_after_bytes=BPS) as server:
            session = make_session(server, buffer={"max_replay_seconds": 0.0})
            async with session:
                await session.append(seconds(1.0))  # server drops at 1s
                await collect_until(session, lambda evs: any(isinstance(e, Reconnected) for e in evs), timeout=10.0)
                assert len(server.connections) == 2
                assert len(server.connections[1].audio) == 0  # nothing replayed
                await session.append(seconds(0.25))
                await asyncio.wait_for(self._wait_bytes(server, 1, int(0.25 * BPS)), 5.0)

    @staticmethod
    async def _wait_bytes(server: FakeRealtimeServer, conn: int, nbytes: int) -> None:
        while len(server.connections) <= conn or len(server.connections[conn].audio) < nbytes:
            await asyncio.sleep(0.01)

    @staticmethod
    async def _wait_bytes_stable(server: FakeRealtimeServer, conn: int, min_bytes: int, timeout: float = 5.0) -> int:
        """Wait for at least min_bytes on a connection, then for the count to go quiet."""
        await asyncio.wait_for(TestReconnect._wait_bytes(server, conn, min_bytes), timeout)
        prev = -1
        while prev != len(server.connections[conn].audio):
            prev = len(server.connections[conn].audio)
            await asyncio.sleep(0.1)
        return prev

    async def test_commit_resent_after_drop(self) -> None:
        async with FakeRealtimeServer(drop_after_bytes=int(0.5 * BPS)) as server:
            session = make_session(server, turn_detection={"type": "none"})
            async with session:
                await session.append(seconds(0.5))
                await session.commit()  # server drops before answering
                events = await collect_until(
                    session,
                    lambda evs: any(isinstance(e, TranscriptCompleted) for e in evs),
                    timeout=10.0,
                )
            assert len(server.connections) == 2
            second = server.connections[1]
            assert second.commits == 1  # the outstanding commit was re-issued
            assert len(second.audio) == len(seconds(0.5))  # full unacked audio replayed
            finals = [e for e in events if isinstance(e, TranscriptCompleted)]
            assert finals and finals[0].replayed is True

    async def test_replayed_flag_set_on_replay_events(self) -> None:
        async with FakeRealtimeServer(completed_every_bytes=BPS, drop_after_bytes=int(1.5 * BPS)) as server:
            # explicit pre-roll so the replay window covers the already
            # transcribed first second and the server re-emits its transcript
            session = make_session(server, buffer={"replay_margin": 5.0})
            async with session:
                await session.append(seconds(1.5))  # 1 completed, then drop
                events = await collect_until(
                    session,
                    lambda evs: sum(isinstance(e, TranscriptCompleted) for e in evs) >= 2,
                    timeout=10.0,
                )
            finals = [e for e in events if isinstance(e, TranscriptCompleted)]
            assert finals[0].replayed is False
            assert finals[1].replayed is True  # produced from replayed audio
            # stable, distinct SDK segment ids despite server item_id reuse patterns
            assert finals[0].segment_id != finals[1].segment_id


class TestTerminalFailureUnderLoad:
    async def test_continuous_appends_during_terminal_failure_do_not_starve_loop(self) -> None:
        """Regression: unsent audio accumulating while a reconnect is in flight
        must not busy-spin the writer and starve the event loop (the reconnect
        task would then never escalate, hanging the session forever)."""
        async with FakeRealtimeServer(drop_after_bytes=int(0.3 * BPS)) as server:
            session = make_session(server, reconnect={"max_attempts": 0})
            with pytest.raises(RealtimeConnectionError):
                async with session:
                    server.reject_statuses.extend([500] * 5)

                    async def feed() -> None:
                        while True:
                            await session.append(seconds(0.1))
                            await asyncio.sleep(0.01)

                    feeder = asyncio.create_task(feed())
                    try:
                        await asyncio.wait_for(collect_until(session, lambda _evs: False, timeout=8.0), 9.0)
                    finally:
                        feeder.cancel()
                        with contextlib.suppress(asyncio.CancelledError, Exception):
                            await feeder


class TestTerminalFailureSurfacesOnCalls:
    async def test_append_and_flush_raise_the_terminal_failure(self) -> None:
        """A plain feed loop must be able to drive failover without a separate
        consumer task: after terminal failure, append()/flush() raise the
        stored RealtimeConnectionError rather than a generic state error."""
        async with FakeRealtimeServer(drop_after_bytes=int(0.2 * BPS)) as server:
            session = make_session(server, reconnect={"max_attempts": 0})
            async with session:
                server.reject_statuses.extend([500] * 5)
                with pytest.raises(RealtimeConnectionError):
                    for _ in range(200):  # keep feeding until failure surfaces
                        await session.append(seconds(0.1))
                        await asyncio.sleep(0.02)
                with pytest.raises(RealtimeConnectionError):
                    await session.flush()


class TestExternalFailover:
    """Endpoint failover is orchestrated OUTSIDE the SDK: on terminal failure
    the app starts a fresh session on an alternate endpoint, seeded with
    pending_audio() and context_prompt() from the failed session."""

    async def test_pending_audio_and_prompt_resume_on_alternate_endpoint(self) -> None:
        async with FakeRealtimeServer(
            completed_every_bytes=BPS, drop_after_bytes=int(2 * BPS)
        ) as primary, FakeRealtimeServer() as alternate:
            session = make_session(
                primary,
                reconnect={"backoff_initial": 0.001, "backoff_max": 0.002, "max_attempts": 2, "max_elapsed": 5.0},
            )
            failed = False
            async with session:
                await session.append(seconds(1.5))
                await collect_until(session, lambda evs: any(isinstance(e, TranscriptCompleted) for e in evs))
                primary.reject_statuses.extend([500] * 20)  # endpoint is now down
                await session.append(seconds(1.0))  # triggers the drop at 2s
                try:
                    await collect_until(session, lambda _evs: False, timeout=10.0)
                except RealtimeConnectionError:
                    failed = True
            assert failed
            # ---- orchestration layer (application code, not the SDK) ----
            pending = session.pending_audio()
            prompt = session.context_prompt()
            assert prompt.startswith("final-") or prompt  # transcript tail available
            # watermark was 1.0s (completed start+duration), head 2.5s
            assert len(pending) == len(seconds(1.5))
            resumed = make_session(alternate, turn_detection={"type": "none"}, prompt=prompt)
            async with resumed:
                await resumed.append(pending)
                await resumed.commit()
                events = await collect_until(resumed, lambda evs: any(isinstance(e, TranscriptCompleted) for e in evs))
            assert len(alternate.connections) == 1
            assert bytes(alternate.connections[0].audio) == pending
            updates = [e for e in alternate.connections[0].events if e["type"] == "transcription_session.updated"]
            assert updates and updates[0]["session"]["prompt"] == prompt
            finals = [e for e in events if isinstance(e, TranscriptCompleted)]
            assert finals


class TestFatalErrors:
    async def test_fatal_model_not_available(self) -> None:
        async with FakeRealtimeServer(
            fatal_error={"message": "no such model", "type": "invalid_request_error", "code": "model_not_available"}
        ) as server:
            session = make_session(server)
            async with session:
                with pytest.raises(RealtimeSessionError) as err:
                    await collect_until(session, lambda _evs: False, timeout=5.0)
                assert err.value.code == "model_not_available"

    async def test_retry_elsewhere_close_code_fails_over_immediately(self) -> None:
        """A 4503 close code makes the SDK fail terminally with
        code='no_healthy_workers' (no same-endpoint reconnect), so a failover
        loop rotates. The JSON frame is informational; the close drives it."""
        async with FakeRealtimeServer(
            fatal_error={"message": "endpoint cannot currently serve", "code": "no_healthy_workers"},
            close_code=4503,
        ) as server:
            # high reconnect budget on purpose: the 4503 close must bypass it
            session = make_session(server, reconnect={"max_attempts": 10})
            async with session:
                with pytest.raises(RealtimeConnectionError) as err:
                    await collect_until(session, lambda _evs: False, timeout=5.0)
            assert err.value.code == "no_healthy_workers"
            # immediate: it did not burn same-endpoint reconnect attempts
            assert len(server.connections) == 1

    async def test_retry_elsewhere_close_code_without_frame_still_fails_over(self) -> None:
        """The close code alone (no JSON frame) is enough to fail over."""
        async with FakeRealtimeServer(close_code=4503, close_without_frame=True) as server:
            session = make_session(server, reconnect={"max_attempts": 10})
            async with session:
                with pytest.raises(RealtimeConnectionError) as err:
                    await collect_until(session, lambda _evs: False, timeout=5.0)
            assert err.value.code == "no_healthy_workers"
            assert len(server.connections) == 1

    async def test_4503_before_session_created_raises_typed_error_on_start(self) -> None:
        """An endpoint unhealthy AT CONNECT TIME closes 4503 before ever
        sending session.created; start() must raise the same typed error a
        failover loop already handles, not a raw websockets exception."""
        async with FakeRealtimeServer(close_code=4503, close_before_created_from=1) as server:
            session = make_session(server)
            with pytest.raises(RealtimeConnectionError) as err:
                await session.start()
            await session.close()
            assert err.value.code == "no_healthy_workers"

    async def test_other_close_before_session_created_raises_typed_error(self) -> None:
        """Any pre-session.created close surfaces as RealtimeConnectionError
        (code-less), never as a leaked websockets.ConnectionClosed."""
        async with FakeRealtimeServer(close_code=1013, close_before_created_from=1) as server:
            session = make_session(server)
            with pytest.raises(RealtimeConnectionError) as err:
                await session.start()
            await session.close()
            assert err.value.code is None

    async def test_4503_before_session_created_on_reconnect_fails_over_immediately(self) -> None:
        """If the endpoint turns unhealthy between a drop and the reconnect
        handshake, the 4503-before-created must fail terminally with the code
        instead of classifying as retryable and burning reconnect attempts."""
        async with FakeRealtimeServer(
            drop_after_bytes=int(0.1 * BPS),
            close_code=4503,
            close_before_created_from=2,
        ) as server:
            session = make_session(server, reconnect={"max_attempts": 10})
            async with session:
                await session.append(seconds(0.2))  # triggers the drop
                with pytest.raises(RealtimeConnectionError) as err:
                    await collect_until(session, lambda _evs: False, timeout=10.0)
            assert err.value.code == "no_healthy_workers"
            # one live connection + one failed reconnect attempt, no retry burn
            assert len(server.connections) == 2

    async def test_initial_handshake_failure_raises_typed_error_naming_target(self) -> None:
        async with FakeRealtimeServer(reject_statuses=[401]) as server:
            session = make_session(server)
            with pytest.raises(RealtimeConnectionError, match="HTTP 401") as err:
                await session.start()
            assert "127.0.0.1" in str(err.value)  # names the target it tried

    async def test_handshake_5xx_retries_then_succeeds(self) -> None:
        async with FakeRealtimeServer(
            completed_every_bytes=BPS, drop_after_bytes=int(0.5 * BPS), reject_statuses=[]
        ) as server:
            # first connection OK; drop; then two 500s on reconnect before success
            session = make_session(server)
            async with session:
                await session.append(seconds(0.25))
                server.reject_statuses.extend([500, 503])
                await session.append(seconds(0.25))  # triggers drop
                events = await collect_until(
                    session, lambda evs: any(isinstance(e, Reconnected) for e in evs), timeout=10.0
                )
            reconnected = [e for e in events if isinstance(e, Reconnected)]
            assert reconnected[0].attempt >= 3  # two rejected handshakes + one success
            assert len(server.connections) == 2

    async def test_retries_exhausted_raises_connection_error(self) -> None:
        async with FakeRealtimeServer(drop_after_bytes=int(0.1 * BPS)) as server:
            session = make_session(
                server,
                reconnect={"backoff_initial": 0.001, "backoff_max": 0.002, "max_attempts": 3, "max_elapsed": 5.0},
            )
            async with session:
                # reject only reconnect attempts, not the initial connect
                server.reject_statuses.extend([500] * 50)
                await session.append(seconds(0.2))
                with pytest.raises(RealtimeConnectionError):
                    await collect_until(session, lambda _evs: False, timeout=10.0)


class TestWatermark:
    async def test_completed_start_duration_bounds_replay(self) -> None:
        # the server reports only half of each segment as transcribed via
        # start+duration, so the watermark (1.5s) trails the anchor (2.0s);
        # replay must start from the watermark minus the margin
        async with FakeRealtimeServer(
            completed_every_bytes=BPS, transcribed_fraction=0.5, drop_after_bytes=int(2.5 * BPS)
        ) as server:
            session = make_session(server, buffer={"replay_margin": 0.5})
            async with session:
                await session.append(seconds(2.0))
                await collect_until(session, lambda evs: sum(isinstance(e, TranscriptCompleted) for e in evs) >= 2)
                assert session.state.watermark == session.state.to_bytes(1.5)  # start 1.0 + duration 0.5
                await session.append(seconds(1.0))
                await collect_until(session, lambda evs: any(isinstance(e, Reconnected) for e in evs), timeout=10.0)
                # watermark 1.5s - margin 0.5s => replay [1.0s, 3.0s] = 2.0s
                replayed = await TestReconnect._wait_bytes_stable(server, 1, int(2.0 * BPS))
            assert replayed == int(2.0 * BPS)


class TestBufferGapEvents:
    async def test_overflow_emits_gap(self) -> None:
        async with FakeRealtimeServer() as server:  # never completes anything
            session = make_session(server, buffer={"max_seconds": 1.0})
            async with session:
                await session.append(seconds(3.0))
                events = await collect_until(
                    session, lambda evs: any(isinstance(e, BufferGap) for e in evs), timeout=5.0
                )
            gaps = [e for e in events if isinstance(e, BufferGap)]
            assert abs(gaps[0].dropped_seconds - 2.0) < 0.1


class TestLifecycleHygiene:
    async def test_pool_registration_tracks_lifecycle(self) -> None:
        # registration happens at start(), not construction: the pool holds a
        # strong reference, so a constructed-but-never-started session must
        # not be pinned by the client-scoped pool forever
        pool = BufferPool()
        async with FakeRealtimeServer() as server:
            session = make_session(server, pool=pool)
            assert session not in pool._holders
            await session.start()
            assert session in pool._holders
            await session.close()
            assert session not in pool._holders

    async def test_failed_start_leaves_no_pool_registration(self) -> None:
        async with FakeRealtimeServer(reject_statuses=[401]) as server:
            pool = BufferPool()
            session = make_session(server, pool=pool)
            with pytest.raises(RealtimeConnectionError):
                await session.start()
            assert session not in pool._holders

    async def test_watchdog_survives_keepalive_append_failure(self, caplog: pytest.LogCaptureFixture) -> None:
        # the keepalive append can raise (overflow='error', stored terminal
        # failure); the watchdog must log and keep probing, not die unobserved
        async with FakeRealtimeServer() as server:
            session = make_session(server, turn_detection={"type": "none"}, keepalive_silence=True)
            await session.start()
            try:
                watchdog = session._watchdog_task
                assert watchdog is not None

                async def _boom(_pcm: bytes) -> None:
                    raise RuntimeError("injected append failure")

                session._last_append_at = session._now() - 300.0  # keepalive due now
                session.append = _boom  # type: ignore[method-assign]
                with caplog.at_level(logging.ERROR, logger="together.realtime"):
                    await asyncio.sleep(1.2)  # a couple of watchdog ticks
                assert not watchdog.done()
                assert any("watchdog iteration failed" in record.message for record in caplog.records)
            finally:
                await session.close()

    async def test_close_awaits_background_tasks(self) -> None:
        # close() must not return with tasks merely cancel()ed but pending:
        # the sync facade stops the loop immediately after, destroying them
        async with FakeRealtimeServer(completed_every_bytes=BPS) as server:
            session = make_session(server)
            await session.start()
            await session.append(seconds(0.1))
            tasks = [
                task
                for task in (session._reader_task, session._writer_task, session._watchdog_task)
                if task is not None
            ]
            assert len(tasks) == 3
            await session.close()
            assert all(task.done() for task in tasks)

    def test_sync_start_failure_stops_loop_thread(self) -> None:
        # a failed start() must tear down the background loop thread instead
        # of stranding it until atexit
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()  # nothing listening: connection refused immediately
        client = AsyncTogether(api_key="test-key", base_url=f"http://127.0.0.1:{port}")
        session = RealtimeTranscriptionSession(client=client, model="openai/whisper-large-v3")
        with pytest.raises(RealtimeConnectionError):
            session.start()
        assert not session._thread.is_alive()
        # the loop must be closed, not merely stopped: a stopped loop leaks
        # its selector/self-pipe fds and emits ResourceWarnings at GC time
        assert session._loop.is_closed()
