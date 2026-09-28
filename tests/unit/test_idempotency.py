from __future__ import annotations

import os
import asyncio
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call, Route

from together import Together, AsyncTogether
from together.lib.beta.rl import SessionClient
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

    assert first_key == "first-operation"
    assert retry_key == first_key
    assert second_call_key == "second-operation"
    assert second_call_key != first_key
    assert caller_key == "caller-provided-key"
    assert IDEMPOTENCY_HEADER not in get_request.headers


@pytest.mark.respx(base_url=BASE_URL)
def test_sync_client_propagates_stable_retry_key(
    client: Together,
    operation_routes: tuple[Route, Route],
) -> None:
    post_route, get_route = operation_routes

    client.beta.rl.operations.create_training_checkpoint("session-id", idempotency_key="first-operation")
    client.beta.rl.operations.create_training_checkpoint("session-id", idempotency_key="second-operation")
    client.beta.rl.operations.create_training_checkpoint(
        "session-id",
        idempotency_key="caller-provided-key",
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

    await async_client.beta.rl.operations.create_training_checkpoint("session-id", idempotency_key="first-operation")
    await async_client.beta.rl.operations.create_training_checkpoint("session-id", idempotency_key="second-operation")
    await async_client.beta.rl.operations.create_training_checkpoint(
        "session-id",
        idempotency_key="caller-provided-key",
    )
    await async_client.beta.rl.operations.retrieve_training_checkpoint(
        OPERATION_ID,
        session_id="session-id",
    )

    _assert_idempotency_headers(post_route, get_route)


_RL_OPERATION_CASES: list[tuple[str, str, dict[str, Any], str, dict[str, Any]]] = [
    ("trainer", "forward", {"samples": [], "loss": {"type": "cross_entropy"}}, "forward-backward", {"loss": 0.0}),
    (
        "trainer",
        "forward_backward",
        {"samples": [], "loss": {"type": "cross_entropy"}},
        "forward-backward",
        {"loss": 0.0},
    ),
    ("trainer", "custom_forward_backward", {"samples": [], "gradients": []}, "custom-forward-backward", {}),
    ("trainer", "optim_step", {}, "optim-step", {"step": 1}),
    ("trainer", "weights_sync", {}, "weights-sync", {"weights_version": 1}),
    (
        "generator",
        "sample",
        {"prompt": {"chunks": []}},
        "sample",
        {"results": [{"sequences": [], "policy_segments": []}]},
    ),
    ("session", "create_inference_checkpoint", {}, "inference-checkpoint", {"model_name": "model"}),
    ("session", "create_training_checkpoint", {}, "training-checkpoint", {"checkpoint_id": "checkpoint"}),
]


@pytest.mark.respx(base_url=BASE_URL)
@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("owner", "method", "kwargs", "endpoint", "output"),
    _RL_OPERATION_CASES,
    ids=[
        "forward",
        "forward-backward",
        "custom-forward-backward",
        "optim-step",
        "weights-sync",
        "sample",
        "inference-checkpoint",
        "training-checkpoint",
    ],
)
async def test_rl_wrappers_generate_retry_keys(
    respx_mock: MockRouter,
    async_mode: bool,
    owner: str,
    method: str,
    kwargs: dict[str, Any],
    endpoint: str,
    output: dict[str, Any],
) -> None:
    path = f"/rl/training-sessions/session-id/operations/{endpoint}"
    post_route = respx_mock.post(path).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(200, json=_pending_operation()),
            httpx.Response(200, json=_pending_operation()),
        ]
    )
    get_route = respx_mock.get(f"{path}/{OPERATION_ID}").mock(
        return_value=httpx.Response(
            200, json={"id": OPERATION_ID, "status": "TRAINING_OPERATION_STATUS_COMPLETED", "output": output}
        )
    )
    session = SessionClient("session-id", _client=AsyncTogether(api_key="test-key", base_url=BASE_URL))
    try:
        resource = session if owner == "session" else getattr(session, owner)
        for _ in range(2):
            if async_mode:
                await getattr(resource, method + "_async")(**kwargs)
            else:
                await asyncio.to_thread(getattr(resource, method), **kwargs)
    finally:
        await session.detach_async()

    keys = [call.request.headers[IDEMPOTENCY_HEADER] for call in cast("list[Call]", post_route.calls)]
    assert len(keys) == 3
    assert keys[0]
    assert keys[0] == keys[1]
    assert keys[2]
    assert keys[0] != keys[2]
    assert get_route.call_count == 2
    assert all(IDEMPOTENCY_HEADER not in call.request.headers for call in cast("list[Call]", get_route.calls))


@pytest.mark.respx(base_url=BASE_URL)
@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "path",
    [
        "/chat/completions",
        "/rl/training-sessions/session-id/stop",
        "/rl/training-sessions/session-id/payloads/upload-url",
    ],
)
async def test_other_posts_do_not_generate_keys(
    client: Together, async_client: AsyncTogether, respx_mock: MockRouter, async_mode: bool, path: str
) -> None:
    route = respx_mock.post(path).mock(return_value=httpx.Response(200, json={}))
    if async_mode:
        await async_client.post(path, cast_to=httpx.Response)
    else:
        client.post(path, cast_to=httpx.Response)
    assert IDEMPOTENCY_HEADER not in cast(Call, route.calls[0]).request.headers
