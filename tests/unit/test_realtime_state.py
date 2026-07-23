from __future__ import annotations

import sys
import threading
from typing import List

import pytest

from together.lib.realtime._state import (
    BufferPool,
    AudioBuffer,
    FailureKind,
    BackoffPolicy,
    RecoveryState,
    iter_frames,
    classify_fatal_error,
    classify_handshake_status,
)
from together.lib.realtime._types import RealtimeErrorInfo
from together.lib.realtime._exceptions import RealtimeBufferOverflowError

BPS = 32_000  # pcm_s16le_16000
FMT = "pcm_s16le_16000"


def seconds(n: float) -> bytes:
    return b"\x01" * int(n * BPS)


def make_state(**kwargs: object) -> RecoveryState:
    # neutral defaults so each test states its intent explicitly; production
    # defaults (margin 0, max_replay_seconds 5) are covered by
    # TestDefaultReplayWindow
    defaults: dict[str, object] = {"input_audio_format": FMT, "replay_margin": 5.0, "max_replay_seconds": None}
    defaults.update(kwargs)
    return RecoveryState(**defaults)  # type: ignore[arg-type]


class TestAudioBuffer:
    def test_append_and_offsets(self) -> None:
        buf = AudioBuffer()
        assert buf.append(b"abc") == 0
        assert buf.append(b"defg") == 3
        assert buf.start_offset == 0
        assert buf.end_offset == 7
        assert buf.size == 7

    def test_trim_mid_chunk_and_read_from(self) -> None:
        buf = AudioBuffer()
        buf.append(b"abcd")
        buf.append(b"efgh")
        freed = buf.trim_to(6)
        assert freed == 6
        assert buf.start_offset == 6
        assert b"".join(buf.read_from(6)) == b"gh"
        # reading below start yields only retained data
        assert b"".join(buf.read_from(0)) == b"gh"

    def test_trim_never_regresses_or_overshoots(self) -> None:
        buf = AudioBuffer()
        buf.append(b"abcd")
        buf.trim_to(2)
        assert buf.trim_to(1) == 0  # regressing is a no-op
        buf.trim_to(100)  # beyond end clamps
        assert buf.size == 0
        assert buf.start_offset == buf.end_offset == 4

    def test_pool_charge_release(self) -> None:
        pool = BufferPool(max_bytes=None)
        buf = AudioBuffer(pool)
        buf.append(b"x" * 100)
        assert pool.used_bytes == 100
        buf.trim_to(40)
        assert pool.used_bytes == 60


class TestBufferPool:
    def test_reclaims_from_largest_holder(self) -> None:
        pool = BufferPool(max_bytes=100)
        state_small = make_state(pool=pool, max_seconds=1000.0)
        state_big = make_state(pool=pool, max_seconds=1000.0)
        pool.register(state_small, lambda: state_small.buffer.size, state_small.reclaim)
        pool.register(state_big, lambda: state_big.buffer.size, state_big.reclaim)

        state_small.record_append(b"a" * 10)
        state_big.record_append(b"b" * 80)
        # pool at 90/100; appending 20 more must reclaim >= 10 from the largest (big)
        state_small.record_append(b"c" * 20)
        assert pool.used_bytes <= 100
        assert state_big.buffer.size < 80
        assert state_small.consume_pending_gap() == 0
        assert state_big.consume_pending_gap() > 0  # un-acked audio was dropped

    def test_cross_thread_reclaim_is_safe_against_owner_iteration(self) -> None:
        """Under pool pressure, charge() reclaims from OTHER sessions' buffers
        on the charging thread — concurrent with those sessions' own event
        loops appending and iterating read_from(). Unsynchronized, this pops
        from a deque mid-iteration (RuntimeError) or corrupts offsets."""
        pool = BufferPool(max_bytes=10_000)
        state_a = make_state(pool=pool, max_seconds=1000.0)
        state_b = make_state(pool=pool, max_seconds=1000.0)
        pool.register(state_a, lambda: state_a.buffer.size, state_a.reclaim)
        pool.register(state_b, lambda: state_b.buffer.size, state_b.reclaim)

        errors: list[BaseException] = []
        stop = threading.Event()

        def hammer_a() -> None:
            # foreign thread: every append keeps the pool saturated, forcing
            # reclaims from state_b (the largest holder) on THIS thread
            try:
                while not stop.is_set():
                    state_a.record_append(b"a" * 256)
            except BaseException as exc:  # pragma: no cover - failure path
                errors.append(exc)

        thread = threading.Thread(target=hammer_a)
        # many small chunks widen the owner's read_from iteration window
        for _ in range(200):
            state_b.record_append(b"b" * 40)
        switch_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)  # force aggressive thread interleaving
        thread.start()
        try:
            for i in range(1_000):
                for _ in range(8):
                    state_b.record_append(b"b" * 40)
                # owner-loop behavior: writer iterating the retained window
                for _chunk in state_b.buffer.read_from(0):
                    pass
                _ = state_b.buffer.size
                # commit-ledger churn: reclaim's _safe_trim_point() does a
                # check-then-min on outstanding_commits, which the owner
                # empties by reassignment (record_completed) and IN PLACE
                # (record_clear) — races here raise ValueError/TypeError
                state_b.record_commit()
                if i % 3 == 0:
                    state_b.record_completed()  # reassigns commits, sets anchor
                if i % 7 == 0:
                    state_b.record_clear()  # clears commits in place, Nones anchor
        except BaseException as exc:  # pragma: no cover - failure path
            errors.append(exc)
        finally:
            stop.set()
            thread.join(timeout=10)
            sys.setswitchinterval(switch_interval)

        assert not errors, f"concurrent reclaim raced: {errors[0]!r}"
        assert state_b.buffer.size == state_b.buffer.end_offset - state_b.buffer.start_offset

    def test_trim_point_and_replay_plan_tolerate_commit_clear_race(self) -> None:
        """The owner loop's record_clear() empties outstanding_commits IN
        PLACE while a cross-thread caller (pool reclaim, sync-facade
        pending_audio) sits between the emptiness check and min(). The
        interleaving window is a few bytecodes, so simulate it
        deterministically: emptiness check triggers the concurrent clear."""

        class VanishingList(List[int]):
            def __bool__(self) -> bool:
                result = len(self) > 0
                self.clear()  # record_clear() lands right after the check
                return result

        for method in ("_safe_trim_point", "replay_plan"):
            state = make_state()
            state.record_append(seconds(10))
            state.record_completed()  # anchor set: the commit floor is reachable
            state.record_commit()
            state.outstanding_commits = VanishingList(state.outstanding_commits)
            getattr(state, method)()  # must not raise ValueError on min([])


class TestClassification:
    def test_handshake(self) -> None:
        assert classify_handshake_status(401) is FailureKind.FATAL_AUTH
        assert classify_handshake_status(403) is FailureKind.FATAL_AUTH
        assert classify_handshake_status(429) is FailureKind.RETRYABLE
        assert classify_handshake_status(500) is FailureKind.RETRYABLE
        assert classify_handshake_status(None) is FailureKind.RETRYABLE

    @pytest.mark.parametrize(
        "error,expected",
        [
            (None, FailureKind.RETRYABLE),
            (RealtimeErrorInfo(code="model_not_available"), FailureKind.FATAL),
            (RealtimeErrorInfo(code="model_not_accessible"), FailureKind.FATAL),
            (RealtimeErrorInfo(code="invalid_api_key"), FailureKind.FATAL_AUTH),
            (RealtimeErrorInfo(code="idle_timeout"), FailureKind.IDLE_TIMEOUT),
            (RealtimeErrorInfo(code="no_healthy_workers"), FailureKind.RETRY_ELSEWHERE),
            (
                RealtimeErrorInfo(type="service_unavailable_error", message="Service unavailable: Timeout"),
                FailureKind.IDLE_TIMEOUT,
            ),
            (
                RealtimeErrorInfo(type="service_unavailable_error", message="Unsupported format: pcm_f32"),
                FailureKind.FATAL,
            ),
            (
                RealtimeErrorInfo(type="service_unavailable_error", message="Unsupported input sample rate 44100"),
                FailureKind.FATAL,
            ),
            (
                RealtimeErrorInfo(type="service_unavailable_error", message="upstream decode failed"),
                FailureKind.RETRYABLE,
            ),
            (RealtimeErrorInfo(type="invalid_request_error", message="bad payload"), FailureKind.FATAL),
        ],
    )
    def test_fatal_frames(self, error: RealtimeErrorInfo, expected: FailureKind) -> None:
        assert classify_fatal_error(error) is expected


class TestBackoff:
    def test_full_jitter_bounds_and_determinism(self) -> None:
        policy = BackoffPolicy(initial=0.5, maximum=15.0, rng=lambda: 1.0)
        assert policy.delay(0) == 0.5
        assert policy.delay(1) == 1.0
        assert policy.delay(10) == 15.0  # capped
        zero = BackoffPolicy(rng=lambda: 0.0)
        assert zero.delay(5) == 0.0


class TestRecoveryAnchor:
    def test_no_events_replays_everything_retained(self) -> None:
        state = make_state()
        state.record_append(seconds(3))
        plan = state.replay_plan()
        assert plan.start_offset == 0
        assert plan.gap_bytes == 0

    def test_anchor_minus_margin(self) -> None:
        state = make_state(replay_margin=5.0)
        state.record_append(seconds(20))
        state.record_completed()  # anchor at 20s
        state.record_append(seconds(4))  # head 24s
        plan = state.replay_plan()
        assert plan.start_offset == state.to_bytes(15.0)  # 20s - 5s margin
        assert plan.gap_bytes == 0

    def test_anchor_trims_buffer(self) -> None:
        state = make_state(replay_margin=5.0)
        state.record_append(seconds(20))
        state.record_completed()
        # retained window is [anchor - margin, head]
        assert state.buffer.start_offset == state.to_bytes(15.0)

    def test_watermark_supersedes_anchor(self) -> None:
        state = make_state(replay_margin=5.0)
        state.begin_epoch(0)
        state.record_append(seconds(20))
        # completed arrives with start+duration covering audio through 18s:
        # watermark (18s) wins over the arrival anchor (20s)
        state.record_completed(processed_seconds=18.0)
        plan = state.replay_plan()
        assert plan.start_offset == state.to_bytes(13.0)  # watermark - margin

    def test_completed_start_duration_sets_watermark(self) -> None:
        # completed.start + duration is the production watermark source
        state = make_state(replay_margin=1.0)
        state.begin_epoch(0)
        state.record_append(seconds(20))
        state.record_completed(processed_seconds=12.0)
        assert state.watermark == state.to_bytes(12.0)
        plan = state.replay_plan()
        # watermark (12s) - margin (1s) wins over anchor (20s) - margin
        assert plan.start_offset == state.to_bytes(11.0)

    def test_completed_watermark_respects_conn_base_across_reconnects(self) -> None:
        state = make_state(replay_margin=0.0)
        state.begin_epoch(0)
        state.record_append(seconds(10))
        state.record_completed(processed_seconds=10.0)
        plan = state.replay_plan()
        state.begin_epoch(plan.start_offset)  # reconnect at 10s global
        state.record_append(seconds(5))  # head 15s; conn timeline restarts
        state.record_completed(processed_seconds=3.0)  # 3s on the NEW connection
        assert state.watermark == state.to_bytes(13.0)  # conn_base 10s + 3s

    def test_watermark_is_monotonic_and_clamped(self) -> None:
        state = make_state()
        state.begin_epoch(0)
        state.record_append(seconds(10))
        state.record_completed(processed_seconds=8.0)
        state.record_completed(processed_seconds=6.0)  # regression ignored
        assert state.watermark == state.to_bytes(8.0)
        state.record_completed(processed_seconds=99.0)  # beyond head clamps to head
        assert state.watermark == state.to_bytes(10.0)

    def test_max_replay_seconds_caps_window_and_reports_gap(self) -> None:
        state = make_state(max_replay_seconds=5.0)
        state.record_append(seconds(60))
        plan = state.replay_plan()
        assert plan.start_offset == state.to_bytes(55.0)
        assert plan.gap_bytes == state.to_bytes(55.0)

    def test_zero_max_replay_seconds_is_pure_resume(self) -> None:
        state = make_state(max_replay_seconds=0.0)
        state.record_append(seconds(30))
        plan = state.replay_plan()
        assert plan.start_offset == state.write_head

    def test_replay_clamped_to_retained_data(self) -> None:
        state = make_state(max_seconds=10.0)  # cap retention at 10s
        state.record_append(seconds(30))  # no completeds: 20s dropped un-acked
        plan = state.replay_plan()
        assert plan.start_offset == state.buffer.start_offset
        # the drop was surfaced at overflow time, not re-reported by the plan
        assert plan.gap_bytes == 0
        assert state.consume_pending_gap() == state.to_bytes(20.0)


class TestDefaultReplayWindow:
    """Replay start = max(head - max_replay_seconds, last transcribed position)."""

    def test_recent_completed_wins(self) -> None:
        state = make_state(replay_margin=0.0, max_replay_seconds=5.0)
        state.record_append(seconds(30))
        state.record_completed(processed_seconds=29.0)  # transcribed through 29s
        state.record_append(seconds(2))  # head 32s
        plan = state.replay_plan()
        # max(32-5=27, 29) = 29: only untranscribed audio replays
        assert plan.start_offset == state.to_bytes(29.0)
        assert plan.gap_bytes == 0

    def test_long_untranscribed_window_capped_with_gap(self) -> None:
        state = make_state(replay_margin=0.0, max_replay_seconds=5.0)
        state.record_append(seconds(30))
        state.record_completed(processed_seconds=10.0)
        state.record_append(seconds(30))  # head 60s; 50s untranscribed
        plan = state.replay_plan()
        # max(60-5=55, 10) = 55: cap wins, 45s of untranscribed audio skipped
        assert plan.start_offset == state.to_bytes(55.0)
        assert plan.gap_bytes == state.to_bytes(45.0)


class TestSampleAlignment:
    """Replay/trim cuts must land on 16-bit sample boundaries: an odd byte
    offset byte-shifts every subsequent sample, turning replayed speech into
    static (whisper hallucinates on it)."""

    def test_watermark_from_fractional_seconds_is_sample_aligned(self) -> None:
        state = make_state(replay_margin=0.0)
        state.begin_epoch(0)
        state.record_append(seconds(3))
        # 1.0000156s * 32000 B/s = 32000.4992 -> int() = 32001, an odd byte
        state.record_completed(processed_seconds=1.0000156)
        assert state.watermark is not None and state.watermark % 2 == 0
        plan = state.replay_plan()
        assert plan.start_offset % 2 == 0

    def test_overflow_trim_keeps_buffer_start_aligned(self) -> None:
        state = make_state(max_seconds=1.0)
        state.record_append(b"\x01" * 32001)  # odd-sized append forces odd excess
        state.record_append(b"\x01" * 32000)
        assert state.buffer.start_offset % 2 == 0
        assert state.replay_plan().start_offset % 2 == 0


class TestOverflow:
    def test_drop_oldest_records_pending_gap(self) -> None:
        state = make_state(max_seconds=10.0)
        state.record_append(seconds(15))
        assert state.buffer.size == state.to_bytes(10.0)
        assert state.consume_pending_gap() == state.to_bytes(5.0)
        assert state.consume_pending_gap() == 0

    def test_acked_trim_is_not_a_gap(self) -> None:
        state = make_state(max_seconds=10.0, replay_margin=0.0)
        state.record_append(seconds(8))
        state.record_completed()  # everything acked; buffer trimmed to anchor
        state.record_append(seconds(9))
        assert state.consume_pending_gap() == 0

    def test_error_policy_raises(self) -> None:
        state = make_state(max_seconds=10.0, overflow="error")
        with pytest.raises(RealtimeBufferOverflowError):
            state.record_append(seconds(15))


class TestCommitLedger:
    def test_commit_retired_by_completed(self) -> None:
        state = make_state()
        state.record_append(seconds(3))
        state.record_commit()
        state.record_append(seconds(1))
        state.record_completed()
        assert state.outstanding_commits == []
        assert state.replay_plan().resend_commit is False

    def test_outstanding_commit_forces_replay_and_resend(self) -> None:
        state = make_state(replay_margin=1.0)
        state.record_append(seconds(10))
        state.record_completed()  # anchor 10s
        state.record_append(seconds(5))
        state.record_commit()  # boundary at 15s, never completed
        state.record_append(seconds(30))
        state.record_completed()  # anchor 45s — but commit at 15s still outstanding?
        # completeds are FIFO: a completed after the commit covers it
        assert state.outstanding_commits == []

    def test_commit_never_completed_keeps_replay_window(self) -> None:
        state = make_state(replay_margin=1.0)
        state.record_append(seconds(10))
        state.record_commit()  # silent tail: server will never answer
        plan = state.replay_plan()
        assert plan.resend_commit is True
        # nothing was ever acked, so the whole retained window replays
        assert plan.start_offset == 0

    def test_outstanding_commit_lowers_anchor_trim(self) -> None:
        state = make_state(replay_margin=1.0)
        state.record_append(seconds(10))
        state.record_completed()  # anchor 10s
        state.record_append(seconds(2))
        state.record_commit()  # boundary 12s
        state.record_append(seconds(20))
        # a completed for OTHER audio must not let trimming pass the commit window
        # (completed retires the commit here per FIFO, so use replay_plan before it)
        plan = state.replay_plan()
        assert plan.start_offset == state.to_bytes(9.0)  # anchor 10s - 1s margin
        assert plan.resend_commit is True

    def test_zero_completed_commit_does_not_block_trimming_forever(self) -> None:
        # A later completed retires older commit boundaries (FIFO ordering),
        # so a 0-completed commit cannot deadlock the ledger.
        state = make_state(replay_margin=0.0)
        state.record_append(seconds(1))
        state.record_commit()
        state.record_append(seconds(20))
        state.record_completed()
        assert state.outstanding_commits == []


class TestEpochsAndSegments:
    def test_begin_epoch_resets_watermark_and_sets_base(self) -> None:
        state = make_state()
        state.begin_epoch(0)
        state.record_append(seconds(10))
        state.record_processed(5_000.0)
        plan = state.replay_plan()
        epoch = state.begin_epoch(plan.start_offset)
        assert epoch == 2
        assert state.watermark is None
        assert state.conn_base == plan.start_offset

    def test_segment_ids_stable_and_globally_unique(self) -> None:
        state = make_state()
        state.begin_epoch(0)
        a = state.segment_for("msg_1", replayed=False)
        assert state.segment_for("msg_1", replayed=False).segment_id == a.segment_id
        state.begin_epoch(0)
        b = state.segment_for("msg_1", replayed=True)  # same server item_id, new epoch
        assert b.segment_id != a.segment_id
        assert b.replayed is True

    def test_anonymous_segments_close_and_rotate(self) -> None:
        state = make_state()
        first = state.segment_for(None, replayed=False)
        state.close_segment(None)
        second = state.segment_for(None, replayed=False)
        assert first.segment_id != second.segment_id

    def test_clear_resets_recovery_state(self) -> None:
        state = make_state()
        state.record_append(seconds(10))
        state.record_commit()
        state.record_completed()
        state.record_clear()
        assert state.buffer.size == 0
        assert state.anchor is None
        assert state.outstanding_commits == []
        assert state.replay_plan().start_offset == state.write_head


class TestFrames:
    def test_iter_frames_exact_and_remainder(self) -> None:
        frames = list(iter_frames(b"x" * 10, 4))
        assert [len(f) for f in frames] == [4, 4, 2]
        assert list(iter_frames(b"", 4)) == []
