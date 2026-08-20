from __future__ import annotations

import os
from typing import Any, cast
from collections.abc import Iterator

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
PENDING_OPERATION = {
    "id": OPERATION_ID,
    "status": "TRAINING_OPERATION_STATUS_PENDING",
}


def _no_retry_delay(*_args: object, **_kwargs: object) -> float:
    return 0.0


@pytest.fixture(autouse=True)
def no_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(BaseClient, "_calculate_retry_timeout", _no_retry_delay)


@pytest.fixture
def operation_routes(respx_mock: MockRouter) -> Iterator[tuple[Route, Route]]:
    post_route = respx_mock.post(OPERATION_PATH).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=PENDING_OPERATION),
            httpx.Response(200, json=PENDING_OPERATION),
            httpx.Response(200, json=PENDING_OPERATION),
        ]
    )
    get_route = respx_mock.get(f"{OPERATION_PATH}/{OPERATION_ID}").mock(
        return_value=httpx.Response(200, json=PENDING_OPERATION)
    )
    yield post_route, get_route


def _assert_idempotency_headers(post_route: Route, get_route: Route) -> None:
    keys: list[str | None] = []
    for index in range(4):
        call = cast(Any, post_route.calls[index])
        request = cast(httpx.Request, call.request)
        keys.append(request.headers.get(IDEMPOTENCY_HEADER))

    get_request = cast(httpx.Request, cast(Any, get_route.calls[0]).request)

    assert keys[0]
    assert keys[0] == keys[1]
    assert keys[2]
    assert keys[2] != keys[0]
    assert keys[3] == "caller-provided-key"
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
