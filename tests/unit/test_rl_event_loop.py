"""Event-loop ownership: one process-wide background loop, many handles of either color."""

from __future__ import annotations

import os
import sys
import types
import select
import signal
import asyncio
import logging
import threading
import traceback
from typing import Any, cast
from collections.abc import Callable
from concurrent.futures import Future, CancelledError

import pytest

from tests.unit._rl_fakes import FakeClient
from together.lib.beta.rl import (
    ModelInput,
    SampleResult,
    SessionClient,
    ModelInputChunk,
    EncodedTextChunk,
    _loop as loop_module,
)
from together.lib.beta.rl._loop import LoopGate, _ProcessLoop, run_untracked, run_untracked_async
from together.lib.beta.rl.clients import (
    session as session_client_module,
    model_resources as model_resources_client_module,
)
from together.types.beta.rl.session import Session
from together.lib.beta.rl.clients.trainer import Trainer
from together.lib.beta.rl.clients.generator import Generator
from together.lib.beta.rl.clients.model_resources import ModelResourcesClient

_PROMPT = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[101, 102]))])


def _make_session() -> SessionClient:
    return SessionClient("sess", _client=cast(Any, FakeClient()))


def _live_loop_threads() -> list[threading.Thread]:
    return [thread for thread in threading.enumerate() if thread.name == "together-rl"]


def _fork_probe(child: Callable[[], object]) -> bytes:
    """Run child() in a fork child.

    Reports b"\\x00" when it returns without raising, b"\\x01" when it raises, and b"" when
    it is still running after 30s — the shape a deadlock regression takes.
    """
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:  # pragma: no cover - child never returns to pytest
        status = 1
        try:
            child()
            status = 0
        except BaseException:
            traceback.print_exc()  # os._exit below would otherwise discard it
        finally:
            try:
                os.write(write_fd, bytes([status]))
            finally:
                os._exit(0)

    os.close(write_fd)
    ready: list[int] = []
    try:
        # The bug under test is a child that hangs forever, so never block on it unbounded.
        ready, _, _ = select.select([read_fd], [], [], 30)
        return os.read(read_fd, 1) if ready else b""
    finally:
        os.close(read_fd)
        if not ready:
            os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)


@pytest.fixture
def polled_loops(monkeypatch: pytest.MonkeyPatch) -> list[asyncio.AbstractEventLoop]:
    """Replace operation polling with a no-op that records where it ran."""
    loops: list[asyncio.AbstractEventLoop] = []

    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        loops.append(asyncio.get_running_loop())
        return types.SimpleNamespace(results=[SampleResult(policy_segments=[], sequences=[])])

    monkeypatch.setattr(SessionClient, "_submit_and_wait", fake)
    return loops


@pytest.mark.parametrize("pool_size", ["0", "\u00b2", "eight"])
def test_a_malformed_pool_size_is_rejected_without_caching_a_loop(
    pool_size: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Publishing the loop before the driver thread would hang every submit after the first."""
    monkeypatch.setenv("TOGETHER_RL_THREAD_POOL_SIZE", pool_size)
    process_loop = _ProcessLoop()
    coro = asyncio.sleep(0)

    with pytest.raises(ValueError, match="TOGETHER_RL_THREAD_POOL_SIZE"):
        process_loop.submit(coro)

    assert process_loop._loop is None
    # Every refusal door closes the coroutine, so a caller never also sees a RuntimeWarning.
    assert coro.cr_frame is None


@pytest.mark.filterwarnings("error::RuntimeWarning")
def test_threads_share_one_session(monkeypatch: pytest.MonkeyPatch) -> None:
    """Many threads share one loop and overlap (barrier would hang if serialized)."""
    loops: list[asyncio.AbstractEventLoop] = []
    all_arrived = asyncio.Event()

    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        loops.append(asyncio.get_running_loop())
        if len(loops) == 8:
            all_arrived.set()
        await asyncio.wait_for(all_arrived.wait(), timeout=5)
        return types.SimpleNamespace(results=[SampleResult(policy_segments=[], sequences=[])])

    monkeypatch.setattr(SessionClient, "_submit_and_wait", fake)
    session = _make_session()
    barrier = threading.Barrier(8)
    results: list[SampleResult] = []
    failures: list[BaseException] = []

    def call() -> None:
        barrier.wait()
        try:
            results.append(session.generator.sample(prompt=_PROMPT))
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=call, daemon=True) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)

    assert not any(thread.is_alive() for thread in threads)
    assert failures == []
    assert len(results) == 8
    assert len(set(loops)) == 1
    session.stop()


def test_async_call_from_a_foreign_loop_runs_on_the_process_loop(
    polled_loops: list[asyncio.AbstractEventLoop],
) -> None:
    session = _make_session()
    session.run(asyncio.sleep(0))
    process_loop = loop_module._process_loop._loop

    caller_loop: list[asyncio.AbstractEventLoop] = []

    async def main() -> SampleResult:
        caller_loop.append(asyncio.get_running_loop())
        return await session.generator.sample_async(prompt=_PROMPT)

    result = asyncio.run(main())

    assert isinstance(result, SampleResult)
    assert polled_loops == [process_loop]
    assert caller_loop[0] is not process_loop
    session.stop()


def test_gather_on_the_process_loop_overlaps(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gathered *_async calls overlap (would hang if serialized)."""
    arrived = 0
    all_arrived = asyncio.Event()

    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        nonlocal arrived
        arrived += 1
        if arrived == 4:
            all_arrived.set()
        await asyncio.wait_for(all_arrived.wait(), timeout=10)
        return types.SimpleNamespace(results=[SampleResult(policy_segments=[], sequences=[])])

    monkeypatch.setattr(SessionClient, "_submit_and_wait", fake)
    session = _make_session()
    session.run(asyncio.sleep(0))

    async def main() -> list[SampleResult]:
        return await asyncio.gather(*(session.generator.sample_async(prompt=_PROMPT) for _ in range(4)))

    results = asyncio.run(main())

    assert len(results) == 4
    session.stop()


def test_repeat_teardown_from_async_is_a_no_op() -> None:
    """run_teardown_async's refusal branch; test_repeat_teardown_is_quiet owns the sync sequences."""
    session = _make_session()
    session.stop()

    assert asyncio.run(session.stop_async()) is None
    assert session._loop.closed


def test_failed_stop_can_be_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed stop must not close the gate — tinker lifecycle retries stop()."""
    session = _make_session()
    attempts = 0

    async def flaky_stop() -> Any:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("remote stop failed")
        return {"id": "stop-op"}

    monkeypatch.setattr(session, "_stop_remote", flaky_stop)

    with pytest.raises(RuntimeError, match="remote stop failed"):
        session.stop()

    assert not session._loop.closed
    assert session.stop() is not None
    assert session._loop.closed
    assert attempts == 2


def test_a_concurrent_stop_joins_the_one_in_flight(monkeypatch: pytest.MonkeyPatch) -> None:
    """The loser of a stop race waits for the winner's session rather than getting None."""
    session = _make_session()
    joined = threading.Event()
    entered = threading.Event()
    claim = session._loop._claim_teardown
    remote_stop = session._stop_remote
    results: list[Any] = []

    def watched(stops_remote: bool) -> tuple[bool, Future[Any] | None]:
        outcome = claim(stops_remote)
        if not outcome[0]:
            joined.set()
        return outcome

    async def slow() -> Any:
        entered.set()
        await asyncio.to_thread(joined.wait, 10)
        return await remote_stop()

    monkeypatch.setattr(session._loop, "_claim_teardown", watched)
    monkeypatch.setattr(session, "_stop_remote", slow)

    def stop() -> None:
        results.append(session.stop())

    winner = threading.Thread(target=stop)
    winner.start()
    assert entered.wait(timeout=10)
    loser = threading.Thread(target=stop)
    loser.start()
    for thread in (winner, loser):
        thread.join(timeout=10)

    assert not any(thread.is_alive() for thread in (winner, loser))
    assert results[0] is not None
    assert results[0] is results[1]
    assert session._loop.closed


def test_stop_cancels_rollout_without_poisoning_the_shared_executor() -> None:
    """stop() cancels this handle's work but leaves the process loop's executor usable."""
    session = _make_session()
    stepping = threading.Event()
    stop_returned = threading.Event()
    outcome: list[BaseException] = []

    def env_step() -> None:
        stepping.set()
        # Held open until stop() has returned, so the step cannot finish first on a slow box.
        stop_returned.wait(timeout=10)

    async def rollout() -> None:
        await asyncio.to_thread(env_step)

    def call() -> None:
        try:
            session.run(rollout())
        except BaseException as exc:
            outcome.append(exc)

    worker = threading.Thread(target=call)
    worker.start()
    assert stepping.wait(timeout=10)

    session.stop()
    stop_returned.set()
    worker.join(timeout=10)

    assert session._loop.closed
    assert len(outcome) == 1
    assert isinstance(outcome[0], CancelledError)

    # Shared executor must still accept work for other handles.
    other = _make_session()

    async def still_works() -> str:
        return await asyncio.to_thread(lambda: "ok")

    assert other.run(still_works()) == "ok"
    other.stop()


@pytest.fixture
def notebook(monkeypatch: pytest.MonkeyPatch) -> None:
    shell = type("ZMQInteractiveShell", (), {})()
    fake = types.SimpleNamespace(get_ipython=lambda: shell)
    monkeypatch.setitem(sys.modules, "IPython", fake)


@pytest.mark.usefixtures("notebook")
def test_blocking_create_in_a_notebook_kernel_uses_the_process_loop(
    polled_loops: list[asyncio.AbstractEventLoop],
) -> None:
    async def build() -> SessionClient:
        return _make_session()

    built: list[SessionClient] = []

    async def cell() -> SampleResult:
        session = run_untracked(build())
        built.append(session)
        return session.generator.sample(prompt=_PROMPT)

    result = asyncio.run(cell())
    session = built[0]

    assert isinstance(result, SampleResult)
    assert not session._loop.closed
    assert polled_loops == [loop_module._process_loop._loop]
    session.stop()


def test_blocking_call_after_stop_says_stopped() -> None:
    session = _make_session()
    session.stop()

    with pytest.raises(RuntimeError, match="stopped or stopping"):
        session.retrieve()


@pytest.mark.parametrize(
    ("module", "construct"),
    [
        (session_client_module, lambda: SessionClient.attach_async(session_id="sess-1")),
        (session_client_module, lambda: SessionClient.create_async(model_resources_id="res-1", interval=0.0)),
        (model_resources_client_module, lambda: ModelResourcesClient.attach_async(model_resources_id="res-1")),
        (model_resources_client_module, lambda: ModelResourcesClient.create_async(base_model="m", interval=0.0)),
    ],
    ids=["session-attach", "session-create", "model_resources-attach", "model_resources-create"],
)
def test_constructors_build_their_client_on_the_process_loop(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    construct: Callable[[], Any],
) -> None:
    """The httpx client must be bound to the loop that will later drive it.

    Built on the caller's loop instead, every subsequent hopped call would drive anyio
    primitives owned by a loop that is by then closed.
    """
    built_on: list[asyncio.AbstractEventLoop] = []

    def fake_together(**_kwargs: Any) -> FakeClient:
        built_on.append(asyncio.get_running_loop())
        return FakeClient()

    monkeypatch.setattr(module, "AsyncTogether", fake_together)
    caller_loop: list[asyncio.AbstractEventLoop] = []

    async def main() -> Any:
        caller_loop.append(asyncio.get_running_loop())
        return await construct()

    handle = asyncio.run(main())

    assert built_on == [loop_module._process_loop._loop]
    assert caller_loop[0] is not loop_module._process_loop._loop
    handle.detach()


def test_async_call_after_stop_refuses_rather_than_running_anywhere() -> None:
    session = _make_session()
    session.stop()

    with pytest.raises(RuntimeError, match="stopped or stopping"):
        asyncio.run(session.retrieve_async())


def test_every_public_async_method_is_hopped_or_deliberately_excluded() -> None:
    """Catch a new public *_async that forgets @on_client_loop (breaks sync-built handles only).

    Marker, not __wrapped__: any functools.wraps decorator would satisfy the latter.
    Constructors hop via run_untracked_async; teardown closes the handle gate; run_async is
    the hop itself.
    """
    excluded = {
        "create_async",
        "attach_async",
        "create_session_async",
        "stop_async",
        "detach_async",
        "run_async",
    }

    missing: list[str] = []
    for client in (SessionClient, Generator, Trainer, ModelResourcesClient):
        for name, method in vars(client).items():
            if not name.endswith("_async") or name.startswith("_") or name in excluded:
                continue
            if not getattr(method, "on_client_loop", False):
                missing.append(f"{client.__name__}.{name}")

    assert missing == [], f"public *_async methods not on the client loop: {missing}"


def test_blocking_call_from_a_plain_running_loop_raises() -> None:
    session = _make_session()

    async def main() -> None:
        session.generator.sample(prompt=_PROMPT)

    with pytest.raises(RuntimeError, match="use the \\*_async variant instead"):
        asyncio.run(main())


def test_two_handles_share_one_process_loop() -> None:
    a = _make_session()
    b = _make_session()

    assert a.run(asyncio.sleep(0, result="a")) == "a"
    assert b.run(asyncio.sleep(0, result="b")) == "b"
    assert len(_live_loop_threads()) == 1

    a.stop()
    assert not b._loop.closed
    assert b.run(asyncio.sleep(0, result="still live")) == "still live"
    b.stop()


@pytest.mark.skipif(not hasattr(os, "fork"), reason="fork is Unix-only")
@pytest.mark.usefixtures("notebook")
def test_blocking_call_from_the_process_loop_refuses_even_in_a_notebook() -> None:
    """A notebook cell may block; code already on the process loop may not — that deadlocks.

    Isolated in a child because a regression here wedges the process loop itself, which no
    in-process timeout can recover: every later test that submits work would hang too.
    """

    def child() -> None:
        session = _make_session()

        async def nested() -> Session:
            return session.retrieve()

        with pytest.raises(RuntimeError, match="use the \\*_async variant instead"):
            session.run(nested())

    assert _fork_probe(child) == b"\x00", "nested blocking call deadlocked the process loop"


@pytest.mark.skipif(not hasattr(os, "fork"), reason="fork is Unix-only")
def test_teardown_from_the_process_loop_refuses_before_claiming_it() -> None:
    """Both endings of a teardown block, so the refusal has to come before the claim.

    A loser that waits on the winner's future from the process loop blocks the one thread that
    could settle it. Isolated in a child because a regression wedges that loop for good.
    """

    def child() -> None:
        session = _make_session()
        tearing_down = threading.Event()
        release = threading.Event()

        async def slow_stop() -> Any:
            tearing_down.set()
            await asyncio.to_thread(release.wait, 10)
            return {"id": "stop-op"}

        async def nested() -> Any:
            return session.stop()

        session._stop_remote = slow_stop  # type: ignore[method-assign]
        winner = threading.Thread(target=session.stop)
        winner.start()
        assert tearing_down.wait(timeout=10)

        try:
            with pytest.raises(RuntimeError, match="use the \\*_async variant instead"):
                run_untracked(nested())
        finally:
            release.set()
            winner.join(timeout=10)

        assert not winner.is_alive()
        assert session._loop.closed

    assert _fork_probe(child) == b"\x00", "a teardown racing from the process loop deadlocked it"


def test_work_is_refused_once_teardown_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sampling submitted mid-stop must not race the remote shutdown."""
    session = _make_session()
    tearing_down = threading.Event()
    release = threading.Event()

    async def slow_stop() -> Any:
        tearing_down.set()
        await asyncio.to_thread(release.wait, 10)
        return {"id": "stop-op"}

    monkeypatch.setattr(session, "_stop_remote", slow_stop)
    stopper = threading.Thread(target=session.stop)
    stopper.start()
    assert tearing_down.wait(timeout=10)

    try:
        with pytest.raises(RuntimeError, match="stopped or stopping"):
            session.retrieve()
    finally:
        release.set()
        stopper.join(timeout=10)

    assert not stopper.is_alive()
    assert session._loop.closed


def _interrupt_the_first_submitted_wait(monkeypatch: pytest.MonkeyPatch, entered: threading.Event) -> None:
    """Raise KeyboardInterrupt out of the blocking wait on the next future submitted to the loop.

    Keyed on that future's identity rather than on call order: a coroutine that hops to the
    default executor also waits on futures, and would otherwise take the interrupt meant for
    the caller.
    """
    submitted: list[Future[Any]] = []
    interrupted: list[Future[Any]] = []
    real_submit = loop_module._process_loop.submit
    real_claim = LoopGate._claim_teardown
    real_result = cast(Any, Future).result

    def submit(coro: Any) -> Future[Any]:
        fut = real_submit(coro)
        submitted.append(fut)
        return fut

    def claim(self: LoopGate, stops_remote: bool) -> tuple[bool, Future[Any] | None]:
        claimed, outcome = real_claim(self, stops_remote)
        if claimed:
            assert outcome is not None
            submitted.append(outcome)
        return claimed, outcome

    def result(self: Future[Any], timeout: float | None = None) -> Any:
        # One-shot, so the reaping wait _blocking_result does after cancelling still runs for real.
        if submitted and self is submitted[0] and not interrupted:
            interrupted.append(self)
            assert entered.wait(timeout=10)
            raise KeyboardInterrupt
        return real_result(self, timeout)

    monkeypatch.setattr(loop_module._process_loop, "submit", submit)
    monkeypatch.setattr(Future, "result", result)
    monkeypatch.setattr(LoopGate, "_claim_teardown", claim)


def test_interrupt_cancels_untracked_work(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ctrl-C during create/attach must not leave construction running on the daemon loop."""
    started = threading.Event()
    cancelled = threading.Event()

    async def slow() -> str:
        started.set()
        try:
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            cancelled.set()
            raise
        return "done"

    _interrupt_the_first_submitted_wait(monkeypatch, started)

    with pytest.raises(KeyboardInterrupt):
        run_untracked(slow())

    assert cancelled.wait(timeout=10)


def test_interrupt_during_stop_cancels_before_reopening_the_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ctrl-C during stop must cancel the remote stop before _abort_teardown reopens the gate."""
    session = _make_session()
    entered = threading.Event()
    cancelled = threading.Event()
    teardown_done: Future[Any] | None = None

    async def slow_stop() -> Any:
        nonlocal teardown_done
        teardown_done = session._loop._teardown_done
        entered.set()
        try:
            await asyncio.sleep(60)
            return {"id": "stop-op"}
        except asyncio.CancelledError:
            cancelled.set()
            raise

    monkeypatch.setattr(session, "_stop_remote", slow_stop)

    _interrupt_the_first_submitted_wait(monkeypatch, entered)

    with pytest.raises(KeyboardInterrupt):
        session.stop()

    assert cancelled.wait(timeout=10)
    assert teardown_done is not None
    # Cancellation is observed before the task-done callback releases the teardown claim.
    with pytest.raises(asyncio.CancelledError):
        teardown_done.result(timeout=10)
    assert not session._loop.closed

    async def finish_stop() -> Any:
        return {"id": "stop-op"}

    monkeypatch.setattr(session, "_stop_remote", finish_stop)
    assert session.stop() is not None
    assert session._loop.closed


def test_detach_then_stop_warns_that_the_remote_is_still_running(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The remote stop is skipped, so it must not be skipped silently."""
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))
    session.detach()

    with caplog.at_level(logging.WARNING, logger="together"):
        assert session.stop() is None

    assert client.beta.rl.sessions.last_stop is None
    assert "keeps running" in caplog.text


@pytest.mark.parametrize(("first", "second"), [("stop", "stop"), ("detach", "detach"), ("stop", "detach")])
def test_repeat_teardown_is_quiet(first: str, second: str, caplog: pytest.LogCaptureFixture) -> None:
    """detach-then-stop is the only sequence that strands the remote; the rest must not warn."""
    session = _make_session()

    with caplog.at_level(logging.WARNING, logger="together"):
        getattr(session, first)()
        getattr(session, second)()

    assert session._loop.closed
    assert caplog.text == ""


@pytest.mark.parametrize("flavor", ["sync", "async"])
@pytest.mark.parametrize(
    ("build_handle", "remote_name"),
    [(SessionClient, "sessions"), (ModelResourcesClient, "model_resources")],
    ids=["session", "model_resources"],
)
def test_context_manager_exit_after_a_detach_is_quiet(
    build_handle: Callable[..., Any],
    remote_name: str,
    flavor: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Exit stops the remote, so it must skip a handle the caller already detached.

    That implicit stop is not the stranded-remote mistake the warning exists for —
    detach is the documented way to leave the remote running. One leg per guarded
    exit method; test_async_context_manager_stops owns the direction that does stop.
    """
    client = FakeClient()
    handle = build_handle("handle", _client=cast(Any, client))

    async def in_async_with() -> None:
        async with handle:
            await handle.detach_async()

    with caplog.at_level(logging.WARNING, logger="together"):
        if flavor == "sync":
            with handle:
                handle.detach()
        else:
            asyncio.run(in_async_with())

    assert handle._loop.closed
    assert caplog.text == ""
    assert getattr(client.beta.rl, remote_name).last_stop is None


@pytest.mark.skipif(not hasattr(os, "fork"), reason="fork is Unix-only")
def test_fork_child_gets_a_fresh_loop() -> None:
    """A child inherits the loop object but not its thread; a new handle must still work."""
    parent = _make_session()
    parent.run(asyncio.sleep(0))

    def child() -> None:
        assert _make_session().run(asyncio.sleep(0, result="ok")) == "ok"

    assert _fork_probe(child) == b"\x00", "fork child hung or failed on a brand-new handle"
    parent.stop()


@pytest.mark.skipif(not hasattr(os, "fork"), reason="fork is Unix-only")
def test_fork_child_is_not_wedged_by_an_inherited_held_lock() -> None:
    """A gate lock inherited while held belongs to a thread the child does not have."""
    session = _make_session()
    session.run(asyncio.sleep(0))

    # As if a peer thread were inside _submit or _forget at the moment of the fork.
    with session._loop._state_lock:
        outcome = _fork_probe(lambda: session._loop._close(None))

    assert outcome == b"\x00", "fork child wedged on a lock inherited while held"
    session.stop()


@pytest.mark.skipif(not hasattr(os, "fork"), reason="fork is Unix-only")
def test_fork_child_is_not_wedged_by_an_inherited_teardown() -> None:
    """A handle forked mid-teardown must not leave the child waiting on the parent's future.

    The child has no thread that can ever settle it, so without the reset the wait is forever.
    The inherited handle stays permanently refusing, which is right: its socket did not survive.
    """
    session = _make_session()
    session.run(asyncio.sleep(0))
    claimed, _ = session._loop._claim_teardown(stops_remote=True)
    assert claimed

    outcome = _fork_probe(lambda: session.stop())

    assert outcome == b"\x00", "fork child wedged waiting on a teardown the parent was driving"
    session._loop._abort_teardown(RuntimeError("no teardown was really driven"))


class _PausedTeardown:
    def __init__(self) -> None:
        self.entered = threading.Event()
        self.cleaning_up = threading.Event()
        self.release_cleanup = threading.Event()
        self.finished_cleanup = threading.Event()
        self.attempts = 0

    async def stop(self) -> str:
        self.attempts += 1
        if self.attempts > 1:
            return "stopped"
        self.entered.set()
        try:
            await asyncio.sleep(60)
            raise AssertionError("teardown was not cancelled")
        finally:
            self.cleaning_up.set()
            assert await asyncio.to_thread(self.release_cleanup.wait, 10)
            self.finished_cleanup.set()


async def _check_gate_during_cleanup(session: SessionClient, teardown: _PausedTeardown) -> None:
    assert await asyncio.to_thread(teardown.cleaning_up.wait, 10)
    assert not teardown.finished_cleanup.is_set()
    with pytest.raises(RuntimeError, match="stopped or stopping"):
        await session.retrieve_async()

    joined = asyncio.Event()

    async def join() -> Any:
        joined.set()
        return await session.stop_async()

    duplicate = asyncio.create_task(join())
    try:
        await joined.wait()
        assert not duplicate.done()
        assert teardown.attempts == 1
        teardown.release_cleanup.set()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(duplicate, 10)
    finally:
        teardown.release_cleanup.set()
        if not duplicate.done():
            duplicate.cancel()
            with pytest.raises(asyncio.CancelledError):
                await duplicate
    assert teardown.finished_cleanup.is_set()
    assert not session._loop.closed
    assert await session.stop_async() == "stopped"
    assert session._loop.closed
    assert teardown.attempts == 2


@pytest.mark.parametrize("process_loop", [False, True], ids=["foreign-loop", "process-loop"])
async def test_cancelled_teardown_holds_gate(monkeypatch: pytest.MonkeyPatch, process_loop: bool) -> None:
    session = _make_session()
    teardown = _PausedTeardown()
    monkeypatch.setattr(session, "_stop_remote", teardown.stop)
    stop = session.stop_async()
    winner = asyncio.create_task(run_untracked_async(stop) if process_loop else stop)
    try:
        assert await asyncio.to_thread(teardown.entered.wait, 10)
        winner.cancel()
        with pytest.raises(asyncio.CancelledError):
            await winner
        await _check_gate_during_cleanup(session, teardown)
    finally:
        teardown.release_cleanup.set()
        if not winner.done():
            winner.cancel()
            with pytest.raises(asyncio.CancelledError):
                await winner


def test_interrupted_teardown_holds_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _make_session()
    teardown = _PausedTeardown()
    monkeypatch.setattr(session, "_stop_remote", teardown.stop)
    _interrupt_the_first_submitted_wait(monkeypatch, teardown.entered)
    try:
        with pytest.raises(KeyboardInterrupt):
            session.stop()
        asyncio.run(_check_gate_during_cleanup(session, teardown))
    finally:
        teardown.release_cleanup.set()
