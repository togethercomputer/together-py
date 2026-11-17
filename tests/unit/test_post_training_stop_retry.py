from __future__ import annotations

import asyncio

import httpx
import pytest

from together import AsyncTogether, InternalServerError
from together.post_training import SessionClient, ModelResourcesClient


@pytest.mark.parametrize(
    ("resource_kind", "failure_method", "expected_calls"),
    [
        ("session", "POST", ["POST", "POST", "GET"]),
        ("session", "GET", ["POST", "GET", "POST", "GET"]),
        ("model_resources", "POST", ["POST", "POST"]),
    ],
)
@pytest.mark.parametrize("synchronous", [False, True])
async def test_stop_retries_transport_failure(
    resource_kind: str, failure_method: str, expected_calls: list[str], synchronous: bool
) -> None:
    calls: list[str] = []
    failed = False
    session = resource_kind == "session"
    pending = "TRAINING_SESSION_STATUS_STOPPING" if session else "MODEL_RESOURCES_STATUS_READY"
    stopped = "TRAINING_SESSION_STATUS_STOPPED" if session else "MODEL_RESOURCES_STATUS_STOPPING"

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal failed
        calls.append(request.method)
        if request.method == failure_method and not failed:
            failed = True
            return httpx.Response(503, json={"message": "Temporary failure"})
        status = pending if request.method == "POST" else stopped
        return httpx.Response(200, json={"id": "resource", "status": status})

    client = AsyncTogether(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)),
    )
    handle = SessionClient("resource", "res", client) if session else ModelResourcesClient("resource", client)
    try:
        with pytest.raises(InternalServerError):
            if synchronous:
                await asyncio.to_thread(handle.stop)
            else:
                await handle.stop_async()

        assert not client.is_closed()
        assert not handle._loop.closed

        if synchronous:
            await asyncio.to_thread(handle.stop)
        else:
            await handle.stop_async()

        assert client.is_closed()
        assert handle._loop.closed
        assert calls == expected_calls
        assert await handle.stop_async() is None
    finally:
        await handle.detach_async()
