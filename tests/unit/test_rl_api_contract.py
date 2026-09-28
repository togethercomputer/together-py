from __future__ import annotations

import json
import asyncio
import inspect
from typing import Any, Optional, get_origin, get_type_hints
from dataclasses import field, dataclass
from typing_extensions import Required

import httpx
import pytest

from together import AsyncTogether
from together._compat import get_model_fields, field_is_required
from together.lib.beta.rl import Sample, Gradient, LossConfig, ModelInput, SessionClient, _payloads
from together.types.beta.rl import (
    operation_sample_params,
    operation_forward_backward_params,
    operation_custom_forward_backward_params,
)
from together.resources.beta.rl.operations import OperationsResource, AsyncOperationsResource
from together.lib.beta.rl.clients.generator import Generator
from together.types.beta.rl.sampled_sequence import SampledSequence

_ROUTING_KEY = "routing/session/0123456789abcdef0123456789abcdef.22"


def test_routing_key_contract() -> None:
    for shape in (Sample, operation_forward_backward_params.Sample, operation_custom_forward_backward_params.Sample):
        hints = get_type_hints(shape, include_extras=True)
        assert set(hints) == {"model_input", "loss_fn_inputs", "routed_experts_key"}
        assert hints["routed_experts_key"] is str
        assert {name for name, hint in hints.items() if get_origin(hint) is Required} == {
            "model_input",
            "loss_fn_inputs",
        }
    sequence_fields = get_model_fields(SampledSequence)
    assert "routed_experts" not in sequence_fields
    assert sequence_fields["routed_experts_key"].annotation == Optional[str]
    assert not field_is_required(sequence_fields["routed_experts_key"])


def test_sampling_parameters() -> None:
    sampling_fields = {
        "model_inputs",
        "sampling_params",
        "num_samples",
        "prompt_logprobs",
        "topk_prompt_logprobs",
        "return_routed_experts",
    }
    assert set(get_type_hints(operation_sample_params.OperationSampleParams)) - {"idempotency_key"} == sampling_fields
    for resource in (OperationsResource, AsyncOperationsResource):
        parameters = inspect.signature(resource.sample).parameters
        assert sampling_fields <= parameters.keys()
        assert "return_routed_experts_object_uri" not in parameters
    for method in (Generator.sample, Generator.sample_async, Generator.sample_batch, Generator.sample_batch_async):
        parameters = inspect.signature(method).parameters
        assert "topk_prompt_logprobs" in parameters
        assert "return_routed_experts" in parameters
        assert "return_routed_experts_object_uri" not in parameters


@dataclass
class _RLTransport:
    requests: list[httpx.Request] = field(default_factory=list[httpx.Request])
    uploads: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.host == "payload.example":
            self.uploads.append(json.loads(request.content))
            assert "Authorization" not in request.headers
            assert "Idempotency-Key" not in request.headers
            return httpx.Response(200)
        if request.url.path.endswith("/payloads/upload-url"):
            assert "Idempotency-Key" not in request.headers
            return httpx.Response(200, json={"payload_id": "payload-1", "upload_url": "https://payload.example/body"})
        operation = request.url.path.split("/operations/")[1].split("/")[0]
        output: dict[str, Any]
        if operation == "sample":
            output = {
                "results": [
                    {
                        "sequences": [
                            {
                                "tokens": [20, 21],
                                "stop_reason": "STOP_REASON_LENGTH",
                                "prompt_cache_hit_tokens": 0,
                                "routed_experts_key": _ROUTING_KEY,
                            }
                        ]
                    }
                ],
            }
        elif operation == "forward-backward":
            output = {"loss": 0.0}
        else:
            assert operation == "custom-forward-backward"
            output = {}
        return httpx.Response(
            200, json={"id": "op-1", "status": "TRAINING_OPERATION_STATUS_COMPLETED", "output": output}
        )


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("batch", [False, True], ids=["single", "batch"])
@pytest.mark.parametrize("large", [False, True], ids=["inline", "r2"])
@pytest.mark.parametrize("custom", [False, True], ids=["loss", "custom-gradient"])
async def test_routing_key_round_trip(
    monkeypatch: pytest.MonkeyPatch, async_mode: bool, batch: bool, large: bool, custom: bool
) -> None:
    transport = _RLTransport()
    client = AsyncTogether(api_key="test-key", http_client=httpx.AsyncClient(transport=httpx.MockTransport(transport)))
    session = SessionClient("session", _client=client)
    prompt = ModelInput(chunks=[{"encoded_text": {"tokens": list(range(20))}}])
    sample_kwargs: dict[str, Any] = {
        "prompts" if batch else "prompt": [prompt] if batch else prompt,
        "return_routed_experts": True,
        "topk_prompt_logprobs": 5,
    }
    try:
        method = "sample_batch" if batch else "sample"
        if async_mode:
            result = await getattr(session.generator, method + "_async")(**sample_kwargs)
        else:
            result = await asyncio.to_thread(getattr(session.generator, method), **sample_kwargs)
        sequence = (result[0] if batch else result).sequences[0]
        assert sequence.routed_experts_key == _ROUTING_KEY
        tokens = list(range(20)) + [int(token) for token in sequence.tokens]
        sample = Sample(
            model_input={"chunks": [{"encoded_text": {"tokens": tokens[:-1]}}]},
            loss_fn_inputs={
                "target_tokens": {"data": tokens[1:], "dtype": "int64"},
                "weights": {"data": [1.0] * (len(tokens) - 1), "dtype": "float32"},
            },
            routed_experts_key=sequence.routed_experts_key,
        )
        if large:
            monkeypatch.setattr(_payloads, "_LARGE_PAYLOAD_THRESHOLD", 1)
        training_kwargs: dict[str, Any] = {"samples": [sample]}
        if custom:
            training_kwargs["gradients"] = [Gradient(data=[0.1] * (len(tokens) - 1), dtype="D_TYPE_FLOAT32")]
        else:
            training_kwargs["loss"] = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")
        method = "custom_forward_backward" if custom else "forward_backward"
        if async_mode:
            await getattr(session.trainer, method + "_async")(**training_kwargs)
        else:
            await asyncio.to_thread(getattr(session.trainer, method), **training_kwargs)
    finally:
        await session.detach_async()

    posts = [
        request for request in transport.requests if request.method == "POST" and "/operations/" in request.url.path
    ]
    assert len(posts) == 2
    assert all(request.headers.get("Idempotency-Key") for request in posts)
    sample_body = json.loads(posts[0].content)
    assert sample_body["return_routed_experts"] is True
    assert sample_body["topk_prompt_logprobs"] == 5
    assert "return_routed_experts_object_uri" not in sample_body
    body = json.loads(posts[1].content)
    assert body["samples"][0]["routed_experts_key"] == _ROUTING_KEY
    assert "routed_experts" not in body["samples"][0]
    if large:
        assert body["payload_id"] == "payload-1"
        assert len(body["samples"][0]["loss_fn_inputs"]["target_tokens"]["data"]) == 8
        assert transport.uploads[0]["samples"] == [sample]
    else:
        assert "payload_id" not in body
        assert not transport.uploads
        assert body["samples"] == [sample]
