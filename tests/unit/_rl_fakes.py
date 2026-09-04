"""Shared in-memory doubles for the RL client tests."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import httpx


class FakeOperations:
    def __init__(self) -> None:
        self.last_call: tuple[str, tuple[Any, ...], dict[str, Any]] | None = None

    async def sample(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("sample", (session_id,), payload)
        return {"id": "sample-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def forward_backward(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("forward_backward", (session_id,), payload)
        return {"id": "fb-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def custom_forward_backward(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("custom_forward_backward", (session_id,), payload)
        return {"id": "cfb-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def optim_step(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("optim_step", (session_id,), payload)
        return {"id": "opt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def weights_sync(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("weights_sync", (session_id,), payload)
        return {"id": "ws-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def create_training_checkpoint(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("create_training_checkpoint", (session_id,), payload)
        return {"id": "train-ckpt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def create_inference_checkpoint(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("create_inference_checkpoint", (session_id,), payload)
        return {"id": "infer-ckpt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}


class FakeSessions:
    def __init__(self) -> None:
        self.last_stop: str | None = None

    async def create(self, **_payload: Any) -> Any:
        return SimpleNamespace(id="sess")

    async def stop(self, session_id: str) -> Any:
        self.last_stop = session_id
        return SimpleNamespace(id="stop-op", status="TRAINING_SESSION_STATUS_STOPPED")

    async def retrieve(self, _session_id: str) -> Any:
        return SimpleNamespace(
            status="TRAINING_SESSION_STATUS_RUNNING",
            resources_id="res-1",
        )


class FakeModelResources:
    def __init__(self) -> None:
        self.num_generator_replicas = 1
        self.last_stop: str | None = None

    async def stop(self, model_resources_id: str, **_payload: Any) -> Any:
        self.last_stop = model_resources_id
        return SimpleNamespace(id="stop-op", status="MODEL_RESOURCES_STATUS_STOPPING")

    async def create(self, **_payload: Any) -> Any:
        return SimpleNamespace(id="res-1")

    async def retrieve(self, _model_resources_id: str) -> Any:
        return SimpleNamespace(
            status="MODEL_RESOURCES_STATUS_READY",
            compute_config=SimpleNamespace(num_generator_replicas=self.num_generator_replicas),
        )


class FakeRL:
    def __init__(self) -> None:
        self.operations = FakeOperations()
        self.sessions = FakeSessions()
        self.model_resources = FakeModelResources()


class FakeBeta:
    def __init__(self) -> None:
        self.rl = FakeRL()


class FakeClient:
    def __init__(self) -> None:
        self.beta = FakeBeta()
        self.closed = False
        self.base_url = httpx.URL("https://api.together.xyz/v1/")
        self.api_key = "test-api-key"
        self.captured_put_body: bytes | None = None

    async def close(self) -> None:
        self.closed = True

    async def post(self, _url: str, **_kwargs: Any) -> dict[str, Any]:
        return {"upload_url": "https://r2.example.com/upload", "payload_id": "pid-123"}

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        self.captured_put_body = kwargs.get("content")
        return httpx.Response(200, request=httpx.Request("PUT", url))
