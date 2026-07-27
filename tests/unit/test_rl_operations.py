from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from together._exceptions import APIStatusError, APIConnectionError
from together.lib.beta.rl import _operations as rl_ops
from together.types.beta.rl.sample_operation import SampleOperation
from together.types.beta.rl.training_operation_error import TrainingOperationError


def _pending() -> SampleOperation:
    return SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING")


def _completed() -> SampleOperation:
    return SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_COMPLETED")


def _status_error(status_code: int) -> APIStatusError:
    request = httpx.Request("GET", "https://api.together.xyz/v1/beta/rl/operations/op-1")
    return APIStatusError("boom", response=httpx.Response(status_code, request=request), body=None)


def _connection_error() -> APIConnectionError:
    return APIConnectionError(request=httpx.Request("GET", "https://api.together.xyz/"))


def _client_returning(*retrievals: Any) -> Any:
    """A client whose `retrieve_sample` yields each entry in turn, raising exceptions."""
    client = MagicMock()
    client.beta.rl.operations.retrieve_sample = AsyncMock(side_effect=list(retrievals))
    return client


def _no_jitter(_low: float, high: float) -> float:
    return high


@pytest.fixture
def slept(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record sleep durations instead of waiting, and freeze jitter to its upper bound."""
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(rl_ops.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(rl_ops.random, "uniform", _no_jitter)
    return delays


async def _wait(client: Any, *, timeout: float | None = 60.0, interval: float = 0.1) -> Any:
    return await rl_ops.async_wait_for_operation(
        client,
        session_id="sess",
        operation=_pending(),
        timeout=timeout,
        interval=interval,
    )


def test_poll_delays_grow_exponentially_and_cap() -> None:
    nominal = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 5.0, 5.0, 5.0]
    delays = rl_ops._poll_delays(0.1)

    assert all(n / 2 <= next(delays) <= n for n in nominal)


def test_poll_delays_are_jittered_within_half_the_interval() -> None:
    delays = rl_ops._poll_delays(rl_ops._MAX_POLL_INTERVAL)
    samples = [next(delays) for _ in range(50)]

    assert all(rl_ops._MAX_POLL_INTERVAL / 2 <= d <= rl_ops._MAX_POLL_INTERVAL for d in samples)
    assert len(set(samples)) > 1


async def test_backs_off_between_polls(slept: list[float]) -> None:
    client = _client_returning(_pending(), _pending(), _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"
    assert slept == [0.1, 0.2, 0.4]  # doubling is exact in binary floating point


@pytest.mark.usefixtures("slept")
@pytest.mark.parametrize("error", [_status_error(408), _status_error(409), _status_error(429), _status_error(503)])
async def test_transient_status_codes_are_treated_as_pending(error: Exception) -> None:
    client = _client_returning(error, _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"


@pytest.mark.usefixtures("slept")
async def test_connection_errors_are_treated_as_pending() -> None:
    client = _client_returning(_connection_error(), _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"


async def test_transient_errors_keep_backing_off(slept: list[float]) -> None:
    client = _client_returning(_status_error(429), _status_error(429), _completed())

    await _wait(client)

    assert slept == [0.1, 0.2, 0.4]  # doubling is exact in binary floating point


@pytest.mark.usefixtures("slept")
@pytest.mark.parametrize("error", [_status_error(400), _status_error(401), _status_error(404), _status_error(422)])
async def test_genuine_errors_fail_fast(error: Exception) -> None:
    client = _client_returning(error)

    with pytest.raises(APIStatusError):
        await _wait(client)


async def test_persistent_transient_errors_time_out_with_cause(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sleeping advances a fake clock so the wall-clock budget is what ends the wait."""
    now = 0.0

    async def fake_sleep(delay: float) -> None:
        nonlocal now
        now += delay

    monkeypatch.setattr(rl_ops.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(rl_ops.time, "monotonic", lambda: now)
    client = MagicMock()
    client.beta.rl.operations.retrieve_sample = AsyncMock(side_effect=_status_error(429))

    with pytest.raises(TimeoutError) as excinfo:
        await _wait(client, timeout=30.0)

    assert isinstance(excinfo.value.__cause__, APIStatusError)


async def test_operation_failure_raises_immediately() -> None:
    failed = SampleOperation(
        id="op-1",
        status="TRAINING_OPERATION_STATUS_FAILED",
        error=TrainingOperationError(message="kaboom"),
    )

    with pytest.raises(RuntimeError, match="kaboom"):
        await rl_ops.async_wait_for_operation(
            cast(Any, MagicMock()),
            session_id="sess",
            operation=failed,
            timeout=60.0,
            interval=0.1,
        )
