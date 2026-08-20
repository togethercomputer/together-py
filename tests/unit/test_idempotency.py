from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Route

from together import Together, AsyncTogether
from together._base_client import BaseClient

BASE_URL = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
IDEMPOTENCY_HEADER = "Idempotency-Key"
OPERATION_ID = "550e8400-e29b-41d4-a716-446655440000"
OPERATION_PATH = "/rl/training-sessions/session-id/operations/training-checkpoint"


def _no_retry_delay(*_args: object, **_kwargs: object) -> float:
    return 0.0


def _pending_operation() -> dict[str, str]:
    return {
        "id": OPERATION_ID,
        "status": "TRAINING_OPERATION_STATUS_PENDING",
    }


@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BaseClient, "_calculate_retry_timeout", _no_retry_delay)


@pytest.fixture
def operation_routes(respx_mock: MockRouter) -> tuple[Route, Route]:
    post_route = respx_mock.post(OPERATION_PATH).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=_pending_operation()),
            httpx.Response(200, json=_pending_operation()),
            httpx.Response(200, json=_pending_operation()),
        ]
    )
    get_route = respx_mock.get(f"{OPERATION_PATH}/{OPERATION_ID}").mock(
        return_value=httpx.Response(200, json=_pending_operation())
    )
    return post_route, get_route


def _assert_idempotency_headers(post_route: Route, get_route: Route) -> None:
    post_calls = cast(tuple[Any, ...], post_route.calls)
    post_keys = tuple(cast(httpx.Request, call.request).headers.get(IDEMPOTENCY_HEADER) for call in post_calls)
    assert len(post_keys) == 4
    first_key, retry_key, second_call_key, caller_key = post_keys
    get_request = cast(httpx.Request, cast(Any, get_route.calls[0]).request)

    assert first_key
    assert retry_key == first_key
    assert second_call_key
    assert second_call_key != first_key
    assert caller_key == "caller-provided-key"
    assert IDEMPOTENCY_HEADER not in get_request.headers


@pytest.mark.respx(base_url=BASE_URL)
def test_sync_client_propagates_stable_retry_key(
    client: Together,
    operation_routes: tuple[Route, Route],
) -> None:
    post_route, get_route = operation_routes

    client.beta.rl.operations.create_training_checkpoint("session-id")
    client.beta.rl.operations.create_training_checkpoint("session-id")
    client.beta.rl.operations.create_training_checkpoint(
        "session-id",
        extra_headers={IDEMPOTENCY_HEADER.lower(): "caller-provided-key"},
    )
    client.beta.rl.operations.retrieve_training_checkpoint(
        OPERATION_ID,
        session_id="session-id",
    )

    _assert_idempotency_headers(post_route, get_route)


@pytest.mark.respx(base_url=BASE_URL)
async def test_async_client_propagates_stable_retry_key(
    async_client: AsyncTogether,
    operation_routes: tuple[Route, Route],
) -> None:
    post_route, get_route = operation_routes

    await async_client.beta.rl.operations.create_training_checkpoint("session-id")
    await async_client.beta.rl.operations.create_training_checkpoint("session-id")
    await async_client.beta.rl.operations.create_training_checkpoint(
        "session-id",
        extra_headers={IDEMPOTENCY_HEADER.lower(): "caller-provided-key"},
    )
    await async_client.beta.rl.operations.retrieve_training_checkpoint(
        OPERATION_ID,
        session_id="session-id",
    )

    _assert_idempotency_headers(post_route, get_route)
