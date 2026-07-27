from __future__ import annotations

from typing import Any, Mapping
from unittest.mock import AsyncMock

import httpx
import pytest

from together._client import AsyncTogether
from together._exceptions import APIStatusError, APITimeoutError, APIConnectionError
from together.lib.beta.rl import _operations as rl_ops
from together.types.beta.rl.sample_operation import SampleOperation
from together.types.beta.rl.training_operation_error import TrainingOperationError


def _pending() -> SampleOperation:
    return SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING")


def _completed() -> SampleOperation:
    return SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_COMPLETED")


def _status_error(status_code: int, headers: Mapping[str, str] | None = None) -> APIStatusError:
    request = httpx.Request("GET", "https://api.together.xyz/v1/beta/rl/operations/op-1")
    response = httpx.Response(status_code, request=request, headers=headers)
    return APIStatusError("boom", response=response, body=None)


def _upper_bound(_low: float, high: float) -> float:
    return high


def _connection_error() -> APIConnectionError:
    return APIConnectionError(request=httpx.Request("GET", "https://api.together.xyz/"))


def _timeout_error() -> APITimeoutError:
    return APITimeoutError(request=httpx.Request("GET", "https://api.together.xyz/"))


def _client_polling(*retrievals: Any) -> AsyncTogether:
    """A real client — so the poll loop exercises its actual retry classification —
    whose operation retrievals yield each entry in turn, raising any that are exceptions."""
    client = AsyncTogether(api_key="test-api-key", base_url="http://127.0.0.1:4010")
    client.beta.rl.operations.retrieve_sample = AsyncMock(  # type: ignore[method-assign]
        side_effect=list(retrievals) or None,
        return_value=_pending(),
    )
    return client


async def _wait(client: AsyncTogether, *, timeout: float | None = 60.0, interval: float = 0.1) -> Any:
    return await rl_ops.async_wait_for_operation(
        client,
        session_id="sess",
        operation=_pending(),
        timeout=timeout,
        interval=interval,
    )


@pytest.fixture
def slept(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record sleep durations instead of waiting, and freeze jitter to its upper bound."""
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(rl_ops.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(rl_ops.random, "uniform", _upper_bound)
    return delays


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
    client = _client_polling(_pending(), _pending(), _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"
    assert slept == [0.1, 0.2, 0.4]  # doubling is exact in binary floating point


@pytest.mark.usefixtures("slept")
@pytest.mark.parametrize("status_code", [408, 409, 429, 500, 503])
async def test_retryable_status_codes_are_treated_as_pending(status_code: int) -> None:
    client = _client_polling(_status_error(status_code), _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"


@pytest.mark.usefixtures("slept")
@pytest.mark.parametrize("error", [_connection_error(), _timeout_error()])
async def test_connection_errors_are_treated_as_pending(error: Exception) -> None:
    client = _client_polling(error, _completed())

    result = await _wait(client)

    assert result.status == "TRAINING_OPERATION_STATUS_COMPLETED"


async def test_failed_polls_keep_backing_off(slept: list[float]) -> None:
    client = _client_polling(_status_error(429), _status_error(429), _completed())

    await _wait(client)

    assert slept == [0.1, 0.2, 0.4]  # doubling is exact in binary floating point


@pytest.mark.usefixtures("slept")
@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 422])
async def test_genuine_errors_fail_fast(status_code: int) -> None:
    client = _client_polling(_status_error(status_code))

    with pytest.raises(APIStatusError):
        await _wait(client)


@pytest.mark.usefixtures("slept")
async def test_x_should_retry_header_overrides_the_status_code() -> None:
    """Retryability is the client's call, so its non-standard override applies here too."""
    stop = _client_polling(_status_error(429, {"x-should-retry": "false"}))
    keep_going = _client_polling(_status_error(400, {"x-should-retry": "true"}), _completed())

    with pytest.raises(APIStatusError):
        await _wait(stop)
    assert (await _wait(keep_going)).status == "TRAINING_OPERATION_STATUS_COMPLETED"


async def test_persistent_failures_time_out_with_cause(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sleeping advances a fake clock so the wall-clock budget is what ends the wait."""
    now = 0.0

    async def fake_sleep(delay: float) -> None:
        nonlocal now
        now += delay

    monkeypatch.setattr(rl_ops.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(rl_ops.time, "monotonic", lambda: now)
    client = _client_polling(*[_status_error(429)] * 100)

    with pytest.raises(TimeoutError) as excinfo:
        await _wait(client, timeout=30.0)

    assert isinstance(excinfo.value.__cause__, APIStatusError)
    assert abs(now - 30.0) < 1e-6


async def test_timeout_is_not_overshot_by_a_pending_operation(monkeypatch: pytest.MonkeyPatch) -> None:
    now = 0.0

    async def fake_sleep(delay: float) -> None:
        nonlocal now
        now += delay

    monkeypatch.setattr(rl_ops.asyncio, "sleep", fake_sleep)
    monkeypatch.setattr(rl_ops.time, "monotonic", lambda: now)
    client = _client_polling()  # always pending

    with pytest.raises(TimeoutError):
        await _wait(client, timeout=8.0)

    assert abs(now - 8.0) < 1e-6


async def test_operation_failure_raises_immediately() -> None:
    failed = SampleOperation(
        id="op-1",
        status="TRAINING_OPERATION_STATUS_FAILED",
        error=TrainingOperationError(message="kaboom"),
    )

    with pytest.raises(RuntimeError, match="kaboom"):
        await rl_ops.async_wait_for_operation(
            _client_polling(),
            session_id="sess",
            operation=failed,
            timeout=60.0,
            interval=0.1,
        )
