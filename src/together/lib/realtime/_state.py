from __future__ import annotations

import enum
import random
import threading
from typing import Dict, List, Deque, Tuple, Callable, Iterator, Optional
from collections import deque
from dataclasses import dataclass

from ._types import (
    RealtimeErrorInfo,
    bytes_per_second,
)
from ._exceptions import RealtimeBufferOverflowError

__all__ = [
    "FailureKind",
    "classify_handshake_status",
    "classify_fatal_error",
    "BackoffPolicy",
    "BufferPool",
    "AudioBuffer",
    "ReplayPlan",
    "SegmentInfo",
    "SessionMetrics",
    "RecoveryState",
    "iter_frames",
]


# ---------------------------------------------------------------------------
# Failure classification
#
# The server always closes with WS code 1000, so fatal-vs-retryable must be
# derived from (a) the HTTP status of a failed handshake and (b) the last
# fatal `...transcription.failed` frame's error payload. Some fatal
# conditions (bad audio format) are wrapped in a generic
# `service_unavailable_error` and are only identifiable by message text.
# ---------------------------------------------------------------------------


class FailureKind(enum.Enum):
    RETRYABLE = "retryable"
    RETRY_ELSEWHERE = "retry_elsewhere"
    FATAL = "fatal"
    FATAL_AUTH = "fatal_auth"
    IDLE_TIMEOUT = "idle_timeout"


_FATAL_CODES = {"model_not_available", "model_not_accessible"}
_AUTH_CODES = {"invalid_api_key", "missing_api_key"}
# Server-reported reasons that mean this endpoint cannot currently serve, so
# retrying it is futile — fail over to another endpoint immediately.
_RETRY_ELSEWHERE_CODES = {"no_healthy_workers"}
_FATAL_MESSAGE_MARKERS = (
    "unsupported format",
    "unsupported input sample rate",
    "invalid audio data format",
)
_IDLE_TIMEOUT_CODES = {"idle_timeout"}


def classify_handshake_status(status_code: Optional[int]) -> FailureKind:
    """Classify a failed WebSocket handshake by its HTTP status (None = network error)."""
    if status_code in (401, 403):
        return FailureKind.FATAL_AUTH
    # 429 and 5xx are transient; unknown statuses default to retryable so that a
    # flaky proxy can't permanently kill a session.
    return FailureKind.RETRYABLE


def classify_fatal_error(error: Optional[RealtimeErrorInfo]) -> FailureKind:
    """Classify the error payload of a fatal `failed` frame (or a bare close)."""
    if error is None:
        return FailureKind.RETRYABLE

    code = (error.code or "").lower()
    if code in _AUTH_CODES:
        return FailureKind.FATAL_AUTH
    if code in _FATAL_CODES:
        return FailureKind.FATAL
    if code in _RETRY_ELSEWHERE_CODES:
        return FailureKind.RETRY_ELSEWHERE
    if code in _IDLE_TIMEOUT_CODES:
        return FailureKind.IDLE_TIMEOUT

    message = (error.message or "").lower()
    if any(marker in message for marker in _FATAL_MESSAGE_MARKERS):
        return FailureKind.FATAL
    # The realtime idle-timeout path currently surfaces as a generic
    # service_unavailable_error with "Timeout" in the message.
    if "timeout" in message and (error.type or "") in ("service_unavailable_error", "request_timeout", ""):
        return FailureKind.IDLE_TIMEOUT

    if (error.type or "") == "invalid_request_error":
        return FailureKind.FATAL
    return FailureKind.RETRYABLE


# ---------------------------------------------------------------------------
# Backoff
# ---------------------------------------------------------------------------


@dataclass
class BackoffPolicy:
    """Exponential backoff with full jitter and deterministic-test injection."""

    initial: float = 0.5
    maximum: float = 15.0
    max_attempts: int = 2
    max_elapsed: float = 120.0
    rng: Callable[[], float] = random.random  # returns [0, 1)

    def delay(self, attempt: int) -> float:
        """Full-jitter delay for a 0-indexed attempt number."""
        cap = min(self.maximum, self.initial * (2.0**attempt))
        return cap * self.rng()


# ---------------------------------------------------------------------------
# Global buffer pool
#
# One pool per client bounds total recovery-buffer memory across all sessions
# in the process. On exhaustion it reclaims from the largest holders first;
# each holder's reclaim callback trims its own buffer and surfaces a
# BufferGap to its consumer.
#
# Reclaim callbacks run synchronously on whatever thread called charge() —
# under pressure that is another session's event-loop thread — so holders'
# held_bytes/reclaim callbacks must be thread-safe (AudioBuffer locks
# internally for this).
# ---------------------------------------------------------------------------


class BufferPool:
    def __init__(self, max_bytes: Optional[int] = 256 * 1024 * 1024) -> None:
        self.max_bytes = max_bytes
        self._used = 0
        self._lock = threading.RLock()
        # holder -> (held_bytes_fn, reclaim_fn(bytes_to_free) -> bytes_freed)
        self._holders: Dict[object, Tuple[Callable[[], int], Callable[[int], int]]] = {}

    @property
    def used_bytes(self) -> int:
        return self._used

    def register(self, holder: object, held_bytes: Callable[[], int], reclaim: Callable[[int], int]) -> None:
        with self._lock:
            self._holders[holder] = (held_bytes, reclaim)

    def unregister(self, holder: object) -> None:
        with self._lock:
            self._holders.pop(holder, None)

    def charge(self, n: int) -> None:
        if n <= 0:
            return
        with self._lock:
            if self.max_bytes is not None and self._used + n > self.max_bytes:
                self._reclaim_locked(self._used + n - self.max_bytes)
            self._used += n

    def release(self, n: int) -> None:
        if n <= 0:
            return
        with self._lock:
            self._used = max(0, self._used - n)

    def _reclaim_locked(self, deficit: int) -> None:
        # Largest holders first; each reclaim releases pool bytes via the
        # holder's own buffer, which calls back into release().
        holders = sorted(self._holders.values(), key=lambda h: h[0](), reverse=True)
        for _held, reclaim in holders:
            if deficit <= 0:
                return
            deficit -= reclaim(deficit)


# ---------------------------------------------------------------------------
# Audio ring buffer with global offsets
# ---------------------------------------------------------------------------


class AudioBuffer:
    """Rolling buffer of appended PCM keyed by global byte offsets.

    Offsets are monotonically increasing over the life of the session; the
    buffer retains the byte range [start_offset, end_offset). Raw PCM is
    stored (base64 encoding happens only at send time).

    Thread safety: the pool reclaims from its largest holders on whatever
    thread called charge(), so trim_to() can run concurrently with the owner
    loop's append()/read_from() (and the sync facade calls pending_audio()
    from the caller's thread). All chunk/offset state is guarded by `_lock`;
    pool charge/release happen outside it so the only lock ordering is
    pool lock -> buffer lock, never the reverse.
    """

    def __init__(self, pool: Optional[BufferPool] = None) -> None:
        self._chunks: Deque[Tuple[int, bytes]] = deque()  # (global_offset, data)
        self._start = 0
        self._end = 0
        self._pool = pool
        self._lock = threading.Lock()

    @property
    def start_offset(self) -> int:
        return self._start

    @property
    def end_offset(self) -> int:
        return self._end

    @property
    def size(self) -> int:
        with self._lock:
            return self._end - self._start

    def append(self, data: bytes) -> int:
        """Append PCM bytes; returns the global offset of the first byte."""
        with self._lock:
            offset = self._end
            if data:
                self._chunks.append((offset, data))
                self._end += len(data)
        if data and self._pool is not None:
            self._pool.charge(len(data))
        return offset

    def trim_to(self, offset: int) -> int:
        """Drop retained bytes below `offset`; returns bytes freed."""
        with self._lock:
            target = min(max(offset, self._start), self._end)
            freed = 0
            while self._chunks:
                chunk_start, data = self._chunks[0]
                chunk_end = chunk_start + len(data)
                if chunk_end <= target:
                    self._chunks.popleft()
                    freed += len(data)
                elif chunk_start < target:
                    keep = data[target - chunk_start :]
                    self._chunks[0] = (target, keep)
                    freed += len(data) - len(keep)
                    break
                else:
                    break
            self._start = max(self._start, target)
            if self._chunks:
                # start_offset never exceeds the first retained chunk
                self._start = min(self._start, self._chunks[0][0])
            else:
                self._start = self._end
        if freed and self._pool is not None:
            self._pool.release(freed)
        return freed

    def read_from(self, offset: int) -> Iterator[bytes]:
        """Yield retained data from `offset` (clamped to what's available).

        Iterates a snapshot: a concurrent pool reclaim may popleft/replace
        chunks mid-iteration, and the chunks themselves are immutable bytes.
        """
        with self._lock:
            chunks = list(self._chunks)
        for chunk_start, data in chunks:
            chunk_end = chunk_start + len(data)
            if chunk_end <= offset:
                continue
            if chunk_start >= offset:
                yield data
            else:
                yield data[offset - chunk_start :]

    def clear(self) -> int:
        return self.trim_to(self._end)


# ---------------------------------------------------------------------------
# Recovery state
# ---------------------------------------------------------------------------


@dataclass
class ReplayPlan:
    start_offset: int
    """Global byte offset replay should start from."""
    gap_bytes: int = 0
    """Un-recovered bytes that were lost (trimmed/skipped) before start_offset."""
    resend_commit: bool = False
    """Whether an outstanding manual commit must be re-issued after replay."""


@dataclass
class SegmentInfo:
    segment_id: str
    audio_start: float
    replayed: bool = False


@dataclass
class SessionMetrics:
    """Counters for observability.

    Ownership is split by layer: the state maintains reconnects (via
    begin_epoch), completed/delta counts, buffered/watermark byte gauges and
    gap_bytes; the session layer maintains replayed_bytes (it owns replay).
    """

    reconnects: int = 0
    replayed_bytes: int = 0
    gap_bytes: int = 0
    completed_events: int = 0
    delta_events: int = 0
    buffered_bytes: int = 0
    watermark_lag_bytes: int = 0


_ANON_ITEM = "~anonymous~"


class RecoveryState:
    """Sans-I/O bookkeeping shared by the sync and async transcription sessions.

    The offset line (global appended-audio byte offsets, all sample-aligned):

        0 .. buffer.start <= replay/trim point <= watermark <= anchor <= write_head
                                  |                  |           |          |
                                  |                  |           |          newest appended byte
                                  |                  |           append offset when the last
                                  |                  |           `completed` ARRIVED
                                  |                  transcribed position from the last
                                  |                  completed's start+duration
                                  max(watermark_or_anchor - replay_margin,
                                      write_head - max_replay_seconds)

    `replay_plan` computes the replay start and `_safe_trim_point` the trim
    floor from the same precedence: watermark > anchor > everything retained,
    clamped so outstanding manual commits stay replayable.

    Owns: the audio buffer, the last-completed replay anchor, the optional
    server `processed_ms` watermark, the manual-commit ledger, connection
    epochs, and segment identity. All byte offsets are global (survive
    reconnects); conversions to seconds use the negotiated audio format.
    """

    def __init__(
        self,
        *,
        input_audio_format: str,
        replay_margin: float = 0.0,
        max_replay_seconds: Optional[float] = 5.0,
        max_seconds: float = 120.0,
        overflow: str = "drop_oldest",
        pool: Optional[BufferPool] = None,
    ) -> None:
        self.bps = bytes_per_second(input_audio_format)
        self.block_align = 2  # 16-bit mono PCM: every cut must land on a sample
        self.buffer = AudioBuffer(pool)
        self.replay_margin_bytes = int(replay_margin * self.bps)
        self.max_replay_seconds = max_replay_seconds
        self.max_bytes = int(max_seconds * self.bps)
        self.overflow = overflow

        self.epoch = 0
        self.conn_base = 0  # global offset of the current connection's timeline zero
        self.anchor: Optional[int] = None  # append offset at last completed arrival
        self.watermark: Optional[int] = None  # global offset from processed_ms (supersedes anchor)
        self.outstanding_commits: List[int] = []  # append offsets of un-retired manual commits
        self.metrics = SessionMetrics()
        self.pending_gap_bytes = 0  # overflow-trimmed unsafe bytes not yet surfaced
        # pending_gap_bytes is the one field written off-loop (reclaim() runs on
        # the pool's charging thread); guard it against a racing consume.
        self._gap_lock = threading.Lock()

        self._segments: Dict[Tuple[int, str], SegmentInfo] = {}
        self._next_segment = 0

    # -- unit helpers -------------------------------------------------------

    def to_seconds(self, nbytes: int) -> float:
        return nbytes / self.bps

    def to_bytes(self, seconds: float) -> int:
        return int(seconds * self.bps)

    def _align(self, offset: int) -> int:
        """Align a byte offset down to a sample boundary.

        Replay/trim cuts at odd offsets would byte-shift every subsequent
        16-bit sample, turning replayed speech into static (and poisoning the
        rest of the stream on that connection).
        """
        return max(0, offset - (offset % self.block_align))

    @property
    def write_head(self) -> int:
        return self.buffer.end_offset

    # -- append/commit path -------------------------------------------------

    def record_append(self, data: bytes) -> int:
        offset = self.buffer.append(data)
        self._enforce_cap()
        self.metrics.buffered_bytes = self.buffer.size
        return offset

    def record_commit(self) -> None:
        self.outstanding_commits.append(self.write_head)

    def record_clear(self) -> None:
        # Server drops its buffered audio and resets offsets; mirror that.
        self.buffer.clear()
        self.anchor = None
        self.watermark = None
        self.outstanding_commits.clear()
        self.conn_base = self.write_head

    # -- server event path ---------------------------------------------------

    def record_completed(self, processed_seconds: Optional[float] = None) -> None:
        """Called when a `completed` frame arrives; anchors recovery at 'now'.

        `processed_seconds` is the event's `start + duration` when the server
        provided both: its position on the connection's audio timeline marks
        how much audio has been transcribed. The server derives it from a
        consumed-speech clock (silence gaps are skipped), so it is treated as
        approximate — the replay margin absorbs the drift.
        """
        self.anchor = self.write_head
        self.metrics.completed_events += 1
        if processed_seconds is not None:
            self._advance_watermark(self.conn_base + self.to_bytes(processed_seconds))
        # Commits at or before the anchor are covered (a commit yields 0 or 1
        # completed, and completeds are FIFO — anything later will re-anchor).
        self.outstanding_commits = [c for c in self.outstanding_commits if c > self.anchor]
        self._trim_safe()

    def record_processed(self, processed_ms: float) -> None:
        """Called on an `input_audio_buffer.processed` watermark event, if the
        server ever emits one (not sent today; completed.start+duration is the
        production watermark source)."""
        self._advance_watermark(self.conn_base + int(processed_ms / 1000.0 * self.bps))
        self._trim_safe()

    def _advance_watermark(self, candidate: int) -> None:
        new_mark = self._align(min(candidate, self.write_head))
        self.watermark = new_mark if self.watermark is None else max(self.watermark, new_mark)

    # -- trimming ------------------------------------------------------------

    def _safe_trim_point(self) -> Optional[int]:
        # The watermark rides the server's consumed-speech clock and the
        # anchor includes decode latency; both are approximate, so both keep
        # the replay margin as a safety buffer.
        #
        # Cross-thread callers (pool reclaim, sync-facade pending_audio) race
        # the owner loop's writes: read each field once and snapshot the
        # commit list — record_clear() empties it IN PLACE, so a bare truthy
        # check followed by min() can see it drain in between and raise.
        watermark = self.watermark
        anchor = self.anchor
        if watermark is not None:
            point = watermark - self.replay_margin_bytes
        elif anchor is not None:
            point = anchor - self.replay_margin_bytes
        else:
            return None
        # Never trim past an outstanding manual commit's replay window.
        commits = list(self.outstanding_commits)
        if commits:
            point = min(point, min(commits) - self.replay_margin_bytes)
        return self._align(max(point, 0))

    def _trim_safe(self) -> None:
        point = self._safe_trim_point()
        if point is not None:
            self.buffer.trim_to(point)
        self.metrics.buffered_bytes = self.buffer.size
        if self.watermark is not None:
            self.metrics.watermark_lag_bytes = max(0, self.write_head - self.watermark)

    def _enforce_cap(self) -> None:
        excess = self.buffer.size - self.max_bytes
        if excess <= 0:
            return
        target = self._align(self.buffer.start_offset + excess)
        safe = self._safe_trim_point()
        unsafe_dropped = max(0, target - safe) if safe is not None else excess
        if unsafe_dropped > 0 and self.overflow == "error":
            raise RealtimeBufferOverflowError(
                f"realtime recovery buffer exceeded {self.to_seconds(self.max_bytes):.1f}s "
                f"of retained audio and overflow policy is 'error'",
                dropped_seconds=self.to_seconds(unsafe_dropped),
            )
        self.buffer.trim_to(target)
        if unsafe_dropped > 0:
            # Un-recovered audio was lost; surfaced by the session as BufferGap.
            self._note_gap(unsafe_dropped)

    def reclaim(self, nbytes: int) -> int:
        """Pool-initiated reclamation (correlated-outage pressure). Oldest first.

        Runs on whatever thread charged the pool, concurrent with the owner
        loop. The buffer's own lock makes the trim safe; the watermark/anchor/
        commit reads here may be one event stale, which at worst trims audio
        that just became replay-relevant — accounted for as `unsafe` below and
        surfaced to the owner as a BufferGap.
        """
        target = self._align(min(self.buffer.start_offset + nbytes, self.buffer.end_offset))
        safe = self._safe_trim_point()
        unsafe = max(0, target - safe) if safe is not None else target - self.buffer.start_offset
        freed = self.buffer.trim_to(target)
        if unsafe > 0:
            self._note_gap(unsafe)
        self.metrics.buffered_bytes = self.buffer.size
        return freed

    def _note_gap(self, nbytes: int) -> None:
        with self._gap_lock:
            self.pending_gap_bytes += nbytes
            self.metrics.gap_bytes += nbytes

    def consume_pending_gap(self) -> int:
        with self._gap_lock:
            gap, self.pending_gap_bytes = self.pending_gap_bytes, 0
            return gap

    # -- reconnect -----------------------------------------------------------

    def replay_plan(self) -> ReplayPlan:
        """Compute where replay should start for a fresh connection.

        Replay starts at max(head - max_replay_seconds, last transcribed
        position): never re-send transcribed audio, never replay more than
        `max_replay_seconds` (default 5) — older untranscribed audio is skipped
        and reported as a gap. The transcribed position comes from
        completed.start + duration (watermark), falling back to the completed
        arrival anchor; `replay_margin` (default 0) optionally rewinds further
        for pre-roll. `max_replay_seconds=None` removes the cap.
        """
        # Single reads + commit-list snapshot for the same reason as
        # _safe_trim_point: pending_audio() calls this from the sync facade's
        # caller thread, racing the owner loop's record_clear/record_completed.
        head = self.write_head
        watermark = self.watermark
        anchor = self.anchor
        commits = list(self.outstanding_commits)
        if watermark is not None:
            desired = watermark - self.replay_margin_bytes
        elif anchor is not None:
            desired = anchor - self.replay_margin_bytes
        else:
            desired = self.buffer.start_offset
        if commits:
            desired = min(desired, min(commits) - self.replay_margin_bytes)
        desired = max(desired, 0)

        gap = 0
        if self.max_replay_seconds is not None:
            lag_floor = head - self.to_bytes(self.max_replay_seconds)
            if lag_floor > desired:
                gap += lag_floor - desired
                desired = lag_floor

        if desired < self.buffer.start_offset:
            gap += self.buffer.start_offset - desired
            desired = self.buffer.start_offset
        desired = self._align(desired)

        return ReplayPlan(
            start_offset=desired,
            gap_bytes=gap,
            resend_commit=bool(commits),
        )

    def begin_epoch(self, replay_start: int) -> int:
        """Start a new connection whose server timeline zero is `replay_start`."""
        self.epoch += 1
        self.conn_base = replay_start
        self.watermark = None  # per-connection; re-established by new events
        if self.epoch > 1:
            self.metrics.reconnects += 1
        return self.epoch

    # -- segment identity ----------------------------------------------------

    def segment_for(self, item_id: Optional[str], *, replayed: bool) -> SegmentInfo:
        key = (self.epoch, item_id or _ANON_ITEM)
        info = self._segments.get(key)
        if info is None:
            self._next_segment += 1
            # audio_start approximates the segment's position on the global
            # appended timeline: the last recovery anchor when the segment was
            # first observed (server start/duration are not timeline-reliable).
            start_offset = self.anchor if self.anchor is not None else self.conn_base
            info = SegmentInfo(
                segment_id=f"seg_{self._next_segment}",
                audio_start=self.to_seconds(start_offset),
                replayed=replayed,
            )
            self._segments[key] = info
        return info

    def close_segment(self, item_id: Optional[str]) -> None:
        self._segments.pop((self.epoch, item_id or _ANON_ITEM), None)


# ---------------------------------------------------------------------------
# Frame chunking
# ---------------------------------------------------------------------------


def iter_frames(data: bytes, frame_bytes: int) -> Iterator[bytes]:
    """Split PCM into frames of at most frame_bytes (no padding)."""
    view = memoryview(data)
    for start in range(0, len(view), frame_bytes):
        yield bytes(view[start : start + frame_bytes])
