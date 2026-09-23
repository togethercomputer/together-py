from __future__ import annotations

import sys
import types
import asyncio
import threading
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from tests.unit.rl_wait import patch_wait
from together.lib.beta.rl import SessionClient, _operations as rl_ops
from together.lib.beta.rl._futures import OperationFuture
from together.types.beta.rl.operation_error import OperationError
from together.types.beta.rl.sample_operation import SampleOperation


def _session() -> SessionClient:
    client = SimpleNamespace(close=AsyncMock())
    return SessionClient("sess", _client=cast(Any, client))


def _operation(op_id: str = "op-1") -> SampleOperation:
    return SampleOperation(id=op_id, status="TRAINING_OPERATION_STATUS_PENDING")


async def _identity(completed: Any) -> Any:
    """Resolvers receive the completed operation; most only want its output."""
    return completed.output


@pytest.fixture
def notebook(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand in for the IPython kernel a Jupyter cell runs under."""
    shell = type("ZMQInteractiveShell", (), {})()
    fake = types.ModuleType("IPython")

    def get_ipython() -> Any:
        return shell

    fake.get_ipython = get_ipython  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "IPython", fake)


async def test_collection_defaults_to_no_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, 42)

    future: OperationFuture[int] = OperationFuture(_session(), _operation(), _identity)
    assert future.id == "op-1"
    assert await future.result_async() == 42
    assert timeouts == [None]


async def test_poll_retrieves_before_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """A lazily collected future may be joined long after its operation finished, so the
    first retrieve must not cost a full interval."""
    events: list[str] = []
    responses = iter(
        [
            SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING"),
            SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_COMPLETED"),
        ]
    )

    async def fake_retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        events.append("retrieve")
        return next(responses)

    async def fake_sleep(_delay: float) -> None:
        events.append("sleep")

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", fake_retrieve)

    completed = await rl_ops.async_wait_for_operation(
        cast(Any, None),
        session_id="sess",
        operation=_operation(),
        timeout=None,
        interval=30.0,
        sleep=fake_sleep,
    )

    assert completed.status == "TRAINING_OPERATION_STATUS_COMPLETED"
    assert events == ["retrieve", "sleep", "retrieve"]


@pytest.mark.parametrize(
    ("interval", "expected"),
    [
        # Default: grows from the caller's interval and flattens at the module cap.
        (0.5, [0.5, 1.0, 2.0, 4.0, 5.0, 5.0, 5.0]),
        # An interval wider than the cap is the caller asking to poll *less* often. The
        # ceiling must not pull it back down to 5.0 — that would multiply the request rate
        # of exactly the callers who already told us to back off.
        (30.0, [30.0] * 7),
    ],
)
async def test_poll_backs_off_geometrically_without_outpacing_the_caller(
    monkeypatch: pytest.MonkeyPatch,
    interval: float,
    expected: list[float],
) -> None:
    """Concurrency multiplies poll cost, so a long wait must get cheaper — but the first
    poll still lands at `interval`, keeping a fast operation exactly as responsive."""
    delays: list[float] = []
    polls = 0

    async def fake_retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        nonlocal polls
        polls += 1
        status = "TRAINING_OPERATION_STATUS_COMPLETED" if polls > 7 else "TRAINING_OPERATION_STATUS_PENDING"
        return SampleOperation(id=operation.id, status=status)

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", fake_retrieve)

    await rl_ops.async_wait_for_operation(
        cast(Any, None),
        session_id="sess",
        operation=_operation(),
        timeout=None,
        interval=interval,
        sleep=fake_sleep,
    )

    assert delays == expected
    assert min(delays) >= interval


async def test_backoff_never_sleeps_past_the_caller_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unclamped sleep would run past `timeout` and report it late, so the last sleep is
    trimmed to the remaining budget and the deadline is honoured when it actually expires."""
    clock = 0.0
    delays: list[float] = []

    async def fake_retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        return SampleOperation(id=operation.id, status="TRAINING_OPERATION_STATUS_PENDING")

    async def fake_sleep(delay: float) -> None:
        nonlocal clock
        delays.append(delay)
        clock += delay

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", fake_retrieve)

    with pytest.raises(TimeoutError):
        await rl_ops.async_wait_for_operation(
            cast(Any, None),
            session_id="sess",
            operation=_operation(),
            timeout=10.0,
            interval=1.0,
            sleep=fake_sleep,
            now=lambda: clock,
        )

    assert delays == [1.0, 2.0, 4.0, 3.0]
    assert sum(delays) == pytest.approx(10.0)  # pyright: ignore[reportUnknownMemberType]


async def test_poll_raises_operation_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    """OperationFuture caches this error and nothing else, so the narrower type is the contract."""

    async def fake_retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        return SampleOperation(
            id=operation.id,
            status="TRAINING_OPERATION_STATUS_FAILED",
            error=OperationError(message="boom"),
        )

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", fake_retrieve)

    with pytest.raises(rl_ops.OperationFailedError, match="boom"):
        await rl_ops.async_wait_for_operation(
            cast(Any, None),
            session_id="sess",
            operation=_operation(),
            timeout=None,
            interval=0.0,
        )


def test_foreign_loop_collection_is_concurrent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Futures collected from a foreign loop must poll concurrently, not one at a time."""
    started = 0
    all_arrived = asyncio.Event()

    async def fake_wait(*, operation: Any, **_kwargs: Any) -> Any:
        nonlocal started
        started += 1
        if started == 8:
            all_arrived.set()
        await asyncio.wait_for(all_arrived.wait(), timeout=5)
        return SimpleNamespace(
            id=operation.id,
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output=operation.id,
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)

    # The collection runs on the process loop, not the caller's.
    session = _session()
    futures = [OperationFuture(session, _operation(f"op-{index}"), _identity) for index in range(8)]

    async def collect() -> list[Any]:
        return list(await asyncio.gather(*(future.result_async() for future in futures)))

    try:
        values = asyncio.run(collect())
    finally:
        session.detach()

    assert sorted(values) == [f"op-{index}" for index in range(8)]
    assert started == 8


async def test_gather_resolves_concurrent_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    retrieves: list[str] = []

    async def fake_wait(*, operation: Any, **_kwargs: Any) -> Any:
        retrieves.append(operation.id)
        await asyncio.sleep(0)
        return SimpleNamespace(
            id=operation.id,
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output=operation.id,
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)
    session = _session()

    first: OperationFuture[str] = OperationFuture(session, _operation("a"), _identity)
    second: OperationFuture[str] = OperationFuture(session, _operation("b"), _identity)
    assert [first.id, second.id] == ["a", "b"]
    assert retrieves == []

    values = await asyncio.gather(first, second)
    assert sorted(values) == ["a", "b"]
    assert sorted(retrieves) == ["a", "b"]


async def test_concurrent_collectors_share_one_poll(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two collectors reaching one future must not poll it twice. Separate tasks, not two
    gather arguments: gather deduplicates identical awaitables and would collect once
    however the future behaved."""
    waits = 0

    async def fake_wait(*, operation: Any, **_kwargs: Any) -> Any:
        nonlocal waits
        waits += 1
        await asyncio.sleep(0)
        return SimpleNamespace(
            id=operation.id,
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output=1,
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)

    future = OperationFuture(_session(), _operation(), _identity)
    collectors = [asyncio.create_task(future.result_async()) for _ in range(2)]
    assert await asyncio.gather(*collectors) == [1, 1]
    assert waits == 1


async def test_cached_resolve_skips_second_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, "value")
    resolves = 0

    async def resolve(completed: Any) -> str:
        nonlocal resolves
        resolves += 1
        return cast(str, completed.output)

    future = OperationFuture(_session(), _operation(), resolve)
    assert await future == "value"
    assert await future.result_async() == "value"
    assert len(timeouts) == 1
    assert resolves == 1


async def test_resolve_failure_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    timeouts = patch_wait(monkeypatch, "value")
    resolves = 0

    async def resolve(completed: Any) -> str:
        nonlocal resolves
        resolves += 1
        if resolves == 1:
            raise ValueError("resolver bug")
        return cast(str, completed.output)

    future = OperationFuture(_session(), _operation(), resolve)

    with pytest.raises(ValueError, match="resolver bug"):
        await future
    assert await future == "value"
    assert len(timeouts) == 2
    assert resolves == 2


async def test_failed_operation_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    waits = 0

    async def fake_wait(*, operation: Any, **_kwargs: Any) -> Any:
        nonlocal waits
        waits += 1
        raise rl_ops.OperationFailedError(f"Operation ({operation.id}) failed: boom")

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)

    future = OperationFuture(_session(), _operation("op-fail"), _identity)
    with pytest.raises(rl_ops.OperationFailedError, match="op-fail"):
        await future
    with pytest.raises(rl_ops.OperationFailedError, match="op-fail"):
        await future.result_async()
    assert waits == 1


async def test_transport_error_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    waits = 0

    async def fake_wait(*, operation: Any, **_kwargs: Any) -> Any:
        nonlocal waits
        waits += 1
        if waits == 1:
            raise ConnectionError("transient blip")
        return SimpleNamespace(
            id=operation.id,
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output="ok",
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)
    future = OperationFuture(_session(), _operation(), _identity)

    with pytest.raises(ConnectionError, match="transient"):
        await future
    assert await future == "ok"
    assert waits == 2


async def test_result_inside_running_loop_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, "ok")

    future = OperationFuture(_session(), _operation(), _identity)
    with pytest.raises(RuntimeError, match="running event loop"):
        future.result()


@pytest.mark.usefixtures("notebook")
def test_notebook_result_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """A cell is logically synchronous, and the collection runs on the process loop rather
    than the kernel's, so there is nothing to deadlock."""
    patch_wait(monkeypatch, "ok")
    session = _session()
    future: OperationFuture[str] = OperationFuture(session, _operation(), _identity)

    async def cell() -> str:
        return future.result()

    try:
        assert asyncio.run(cell()) == "ok"
    finally:
        session.detach()


async def test_timeout_includes_lock_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    polling = threading.Event()
    release = threading.Event()

    async def fake_wait(**_kwargs: Any) -> Any:
        polling.set()
        while not release.wait(timeout=0):
            await asyncio.sleep(0)
        return SimpleNamespace(
            id="op-1",
            status="TRAINING_OPERATION_STATUS_COMPLETED",
            output="ok",
            error=None,
        )

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)
    future = OperationFuture(_session(), _operation(), _identity)
    first = asyncio.create_task(future.result_async())
    assert await asyncio.to_thread(polling.wait, 5), "in-flight collector never started polling"

    with pytest.raises(TimeoutError):
        await future.result_async(timeout=0.1)
    release.set()
    assert await first == "ok"


async def test_timeout_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_wait(*, timeout: float | None, **_kwargs: Any) -> Any:
        raise TimeoutError(f"timed out after {timeout}")

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)

    future = OperationFuture(_session(), _operation(), _identity)
    with pytest.raises(TimeoutError, match="timed out after"):
        await future.result_async(1.5)


@pytest.mark.parametrize("stage", ["retrieve", "resolve"])
@pytest.mark.parametrize("sync", [False, True])
async def test_collection_deadline_cancels_and_retries(monkeypatch: pytest.MonkeyPatch, stage: str, sync: bool) -> None:
    cancelled = threading.Event()
    slow = True

    async def pause() -> None:
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled.set()
            raise

    async def retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        if slow and stage == "retrieve":
            await pause()
        return SampleOperation(id=operation.id, status="TRAINING_OPERATION_STATUS_COMPLETED")

    async def resolve(_completed: Any) -> str:
        if slow and stage == "resolve":
            await pause()
        return "ok"

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", retrieve)
    session = _session()
    future = OperationFuture(session, _operation(), resolve)
    try:
        with pytest.raises(TimeoutError, match="Timed out waiting for operation"):
            if sync:
                await asyncio.to_thread(future.result, timeout=0.05)
            else:
                await future.result_async(timeout=0.05)
        assert cancelled.is_set()
        slow = False
        if sync:
            assert await asyncio.to_thread(future.result) == "ok"
        else:
            assert await future.result_async() == "ok"
    finally:
        await session.detach_async()


async def test_collection_shares_one_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    async def retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        await asyncio.sleep(0.1)
        return SampleOperation(id=operation.id, status="TRAINING_OPERATION_STATUS_COMPLETED")

    async def resolve(_completed: Any) -> str:
        await asyncio.sleep(0.1)
        return "ok"

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", retrieve)
    session = _session()
    future = OperationFuture(session, _operation(), resolve)
    try:
        with pytest.raises(TimeoutError):
            await future.result_async(timeout=0.15)
        assert await future.result_async() == "ok"
    finally:
        await session.detach_async()


async def test_poll_deadline_bounds_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    cancelled = False

    async def retrieve(_client: Any, *, session_id: str, operation: Any) -> Any:  # noqa: ARG001
        nonlocal cancelled
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled = True
            raise
        return SampleOperation(id=operation.id, status="TRAINING_OPERATION_STATUS_COMPLETED")

    monkeypatch.setattr(rl_ops, "async_retrieve_operation", retrieve)
    with pytest.raises(TimeoutError, match="Timed out waiting for operation"):
        await rl_ops.async_wait_for_operation(
            cast(Any, None), session_id="sess", operation=_operation(), timeout=0.05, interval=0.5
        )
    assert cancelled
