from __future__ import annotations

import json
import asyncio
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from together.lib.beta.rl import (
    Prompt,
    Sample,
    Logprob,
    Trainer,
    Gradient,
    PromptChunk,
    SampleResult,
    ForwardResult,
    LossMaskParam,
    LossConfigParam,
    LossInputsParam,
    OptimStepResult,
    SampleModelInput,
    MuonOptimizerParams,
    AdamwOptimizerParams,
    ForwardBackwardResult,
    LossTargetTokensParam,
    SampleModelInputChunk,
    PromptChunkEncodedText,
    TrainingCheckpointResult,
    InferenceCheckpointResult,
    SampleModelInputChunkEncodedText,
    trainer as rl_trainer_module,
    _payloads as rl_payloads_module,
    _operations as rl_ops,
)
from together.types.beta.rl.sample_result import Rollout, RolloutSequence
from together.types.beta.rl.sample_operation import SampleOperation


class FakeOperations:
    def __init__(self) -> None:
        self.last_call: tuple[str, tuple[Any, ...], dict[str, Any]] | None = None

    async def sample(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("sample", (session_id,), payload)
        return {"id": "sample-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def forward(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("forward", (session_id,), payload)
        return {"id": "fwd-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def forward_backward(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("forward_backward", (session_id,), payload)
        return {"id": "fb-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def custom_forward_backward(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("custom_forward_backward", (session_id,), payload)
        return {"id": "cfb-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def optim_step(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("optim_step", (session_id,), payload)
        return {"id": "opt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def create_training_checkpoint(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("create_training_checkpoint", (session_id,), payload)
        return {"id": "train-ckpt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}

    async def create_inference_checkpoint(self, session_id: str, **payload: Any) -> dict[str, Any]:
        self.last_call = ("create_inference_checkpoint", (session_id,), payload)
        return {"id": "infer-ckpt-op", "status": "TRAINING_OPERATION_STATUS_PENDING"}


class FakeSessions:
    def __init__(self) -> None:
        self.last_stop: str | None = None
        self.status_value: str | None = "TRAINING_SESSION_STATUS_RUNNING"

    async def stop(self, session_id: str) -> dict[str, Any]:
        self.last_stop = session_id
        return {"id": "stop-op"}

    async def retrieve(self, _session_id: str) -> Any:
        return SimpleNamespace(status=self.status_value)


class FakeRL:
    def __init__(self) -> None:
        self.operations = FakeOperations()
        self.sessions = FakeSessions()


class FakeBeta:
    def __init__(self) -> None:
        self.rl = FakeRL()


class FakeClient:
    def __init__(
        self,
        *,
        upload_response: dict[str, Any] | None = None,
        upload_put_status: int = 200,
    ) -> None:
        self.beta = FakeBeta()
        self.closed = False
        self.base_url = httpx.URL("https://api.together.xyz/v1/")
        self.api_key = "test-api-key"
        self._upload_response: dict[str, Any] = upload_response or {
            "upload_url": "https://r2.example.com/upload",
            "payload_id": "pid-123",
        }
        self._upload_put_status = upload_put_status
        self.captured_put_body: bytes | None = None

    async def close(self) -> None:
        self.closed = True

    async def post(self, _url: str, **_kwargs: Any) -> dict[str, Any]:
        return self._upload_response

    async def put(self, url: str, **kwargs: Any) -> httpx.Response:
        self.captured_put_body = kwargs.get("content")
        return httpx.Response(self._upload_put_status, request=httpx.Request("PUT", url))


def _make_trainer(client: FakeClient | None = None) -> Trainer:
    if client is None:
        client = FakeClient()
    return Trainer("sess", _client=cast(Any, client))


def _patch_submit_and_wait(monkeypatch: pytest.MonkeyPatch, result: Any) -> None:
    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        return result

    monkeypatch.setattr(Trainer, "_submit_and_wait", fake)


def test_sample_wraps_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, SampleResult(rollouts=[]))
    client = FakeClient()
    trainer = _make_trainer(client)

    prompt = Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[101, 102]))])
    result = trainer.sample(prompt, num_samples=3)

    assert result.rollouts == []
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["prompts"] == [prompt]
    trainer.stop()


def test_sample_batch_passes_multiple_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, SampleResult(rollouts=[]))
    client = FakeClient()
    trainer = _make_trainer(client)

    prompts = [
        Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[1, 2]))]),
        Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[3, 4]))]),
    ]
    trainer.sample_batch(prompts)

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["prompts"] == prompts
    trainer.stop()


def test_compute_logprobs_requests_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SampleResult(
        rollouts=[Rollout(sequences=[RolloutSequence(tokens=[1, 2])], prompt_logprobs=[-0.5, -1.5])]
    )
    _patch_submit_and_wait(monkeypatch, result)
    client = FakeClient()
    trainer = _make_trainer(client)

    prompt = Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[1, 2]))])
    logprobs = trainer.compute_logprobs(prompt)

    assert logprobs == [-0.5, -1.5]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["prompts"] == [prompt]
    assert kwargs["num_samples"] == 1
    assert kwargs["sampling_params"]["return_prompt_logprobs"] is True
    assert kwargs["sampling_params"]["max_tokens"] == 1
    trainer.stop()


def test_compute_logprobs_batch_requests_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SampleResult(
        rollouts=[
            Rollout(sequences=[RolloutSequence(tokens=[1, 2])], prompt_logprobs=[-0.5, -1.5]),
            Rollout(sequences=[RolloutSequence(tokens=[3, 4])], prompt_logprobs=[-0.1, -0.2]),
        ]
    )
    _patch_submit_and_wait(monkeypatch, result)
    client = FakeClient()
    trainer = _make_trainer(client)

    prompts = [
        Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[1, 2]))]),
        Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[3, 4]))]),
    ]
    logprobs = trainer.compute_logprobs_batch(prompts)

    assert logprobs == [[-0.5, -1.5], [-0.1, -0.2]]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["prompts"] == prompts
    assert kwargs["num_samples"] == 1
    assert kwargs["sampling_params"]["return_prompt_logprobs"] is True
    assert kwargs["sampling_params"]["max_tokens"] == 1
    trainer.stop()


def test_prompt_logprobs_from_result_raises_when_missing() -> None:
    result = SampleResult(rollouts=[Rollout(sequences=[RolloutSequence(tokens=[1, 2])])])
    with pytest.raises(RuntimeError, match="prompt logprobs"):
        rl_trainer_module._prompt_logprobs_from_result(result)


def test_forward_passes_samples(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(
        monkeypatch,
        ForwardResult(logprobs=[Logprob(data=[-1.0, -2.0, -3.0])]),
    )
    client = FakeClient()
    trainer = _make_trainer(client)

    samples = [_small_sample()]
    result = trainer.forward(samples=samples)

    assert result.logprobs[0].data == [-1.0, -2.0, -3.0]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward"
    assert args == ("sess",)
    assert kwargs["samples"] == samples
    assert kwargs.get("extra_body") is None
    trainer.stop()


def test_custom_forward_backward_passes_samples_and_gradients(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, {"metrics": {"grad_norm": 0.5}})
    client = FakeClient()
    trainer = _make_trainer(client)

    samples = [_small_sample()]
    gradients = [Gradient(data=[0.1, -0.2, 0.3], dtype="D_TYPE_FLOAT32")]
    result = trainer.custom_forward_backward(samples=samples, gradients=gradients)

    assert result == {"metrics": {"grad_norm": 0.5}}
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "custom_forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == samples
    assert kwargs["gradients"] == gradients
    assert kwargs.get("extra_body") is None
    trainer.stop()


def test_forward_backward_passes_samples_and_loss(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    client = FakeClient()
    trainer = _make_trainer(client)

    samples = [
        Sample(
            model_input=SampleModelInput(
                chunks=[
                    SampleModelInputChunk(
                        encoded_text=SampleModelInputChunkEncodedText(
                            tokens=[1, 2, 3],
                        ),
                    )
                ]
            ),
            loss_inputs=LossInputsParam(
                target_tokens=LossTargetTokensParam(data=[1, 2, 3], dtype="D_TYPE_INT64"),
                loss_mask=LossMaskParam(
                    data=[1, 0, 1],
                    dtype="D_TYPE_INT64",
                ),
            ),
        )
    ]
    loss = LossConfigParam(type="LOSS_TYPE_CROSS_ENTROPY")

    result = trainer.forward_backward(samples=samples, loss=loss)

    assert result.loss == 1.0
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == samples
    assert kwargs["loss"] == loss
    trainer.stop()


def test_optim_step_passes_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_trainer(client)

    result = trainer.optim_step(
        adamw_params=AdamwOptimizerParams(beta1=0.9, learning_rate=1e-4),
    )

    assert result.step == "1"
    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["adamw_params"] == {"beta1": 0.9, "learning_rate": 1e-4}
    trainer.stop()


def test_optim_step_forwards_muon_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_trainer(client)

    trainer.optim_step(
        muon_params=MuonOptimizerParams(learning_rate=0.02, momentum=0.95),
    )

    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["muon_params"] == {"learning_rate": 0.02, "momentum": 0.95}
    trainer.stop()


def test_optim_step_forwards_max_grad_norm(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_trainer(client)

    trainer.optim_step(max_grad_norm=1.0)

    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["max_grad_norm"] == 1.0
    trainer.stop()


def test_create_training_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, TrainingCheckpointResult(checkpoint_id="ckpt-1"))
    client = FakeClient()
    trainer = _make_trainer(client)

    result = trainer.create_training_checkpoint()

    assert result.checkpoint_id == "ckpt-1"
    assert client.beta.rl.operations.last_call is not None
    method, args, _ = client.beta.rl.operations.last_call
    assert method == "create_training_checkpoint"
    assert args == ("sess",)
    trainer.stop()


def test_create_inference_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, InferenceCheckpointResult(model_name="model-1"))
    client = FakeClient()
    trainer = _make_trainer(client)

    result = trainer.create_inference_checkpoint()

    assert result.api_model_name == "model-1"
    trainer.stop()


def test_session_property() -> None:
    client = FakeClient()
    trainer = _make_trainer(client)

    session = trainer.session

    assert session.status == "TRAINING_SESSION_STATUS_RUNNING"
    trainer.stop()


def test_stop_closes_client() -> None:
    client = FakeClient()
    trainer = _make_trainer(client)

    trainer.stop()

    assert client.beta.rl.sessions.last_stop == "sess"
    assert client.closed is True


def test_context_manager_stops() -> None:
    client = FakeClient()
    trainer = _make_trainer(client)

    with trainer:
        assert trainer._session_id == "sess"

    assert client.beta.rl.sessions.last_stop == "sess"
    assert client.closed is True


async def test_create_async_attaches_to_model_resources_and_returns_trainer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.create = AsyncMock(return_value=SimpleNamespace(id="sess-1"))
    fake_client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_RUNNING")
    )

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(rl_trainer_module, "AsyncTogether", fake_together)

    trainer = await Trainer.create_async(
        model_resources_id="res-1",
        api_key="api-key",
        base_url="http://127.0.0.1:4010",
        timeout=0.1,
        interval=0.0,
    )

    assert trainer._session_id == "sess-1"
    fake_client.beta.rl.sessions.retrieve.assert_awaited_once_with("sess-1")
    await_args = fake_client.beta.rl.sessions.create.await_args
    assert await_args is not None
    create_kwargs = await_args.kwargs
    assert create_kwargs["model_resources_id"] == "res-1"


async def test_create_async_closes_client_on_terminal_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.create = AsyncMock(return_value=SimpleNamespace(id="sess-1"))
    fake_client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_ERROR")
    )
    fake_client.close = AsyncMock()

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(rl_trainer_module, "AsyncTogether", fake_together)

    with pytest.raises(RuntimeError, match="TRAINING_SESSION_STATUS_ERROR"):
        await Trainer.create_async(
            model_resources_id="res-1",
            api_key="api-key",
            base_url="http://127.0.0.1:4010",
            timeout=0.1,
            interval=0.0,
        )

    fake_client.close.assert_awaited_once()


@pytest.mark.parametrize(
    "status",
    [
        "TRAINING_SESSION_STATUS_STOPPED",
        "TRAINING_SESSION_STATUS_STOPPING",
        "TRAINING_SESSION_STATUS_ERROR",
        "TRAINING_SESSION_STATUS_EXPIRED",
    ],
)
async def test_wait_for_creation_raises_on_terminal_status(status: str) -> None:
    client = MagicMock()
    client.beta.rl.sessions.retrieve = AsyncMock(return_value=SimpleNamespace(status=status))
    trainer = Trainer("sess", _client=cast(Any, client))

    with pytest.raises(RuntimeError, match=status):
        await trainer._wait_for_creation_async(timeout=1.0, interval=0.0)


async def test_wait_for_creation_times_out() -> None:
    client = MagicMock()
    client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_CREATING")
    )
    trainer = Trainer("sess", _client=cast(Any, client))

    with pytest.raises(TimeoutError):
        await trainer._wait_for_creation_async(timeout=0.0, interval=0.0)


async def test_stop_async_closes_client_and_event_loop() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value={"id": "stop-op"})
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    trainer = Trainer("sess", _client=cast(Any, client))
    trainer._event_loop = event_loop

    result = await trainer.stop_async()

    assert result == {"id": "stop-op"}
    assert event_loop.is_closed()
    assert trainer._event_loop is None
    client.beta.rl.sessions.stop.assert_awaited_once_with("sess")
    client.close.assert_awaited_once()


async def test_attach_async_binds_existing_session(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.create = AsyncMock()
    fake_client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_RUNNING")
    )
    fake_client.close = AsyncMock()

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(rl_trainer_module, "AsyncTogether", fake_together)

    trainer = await Trainer.attach_async(session_id="sess-1")

    assert trainer._session_id == "sess-1"
    fake_client.beta.rl.sessions.retrieve.assert_awaited_once_with("sess-1")
    fake_client.beta.rl.sessions.create.assert_not_awaited()
    fake_client.close.assert_not_awaited()


async def test_attach_async_raises_and_closes_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.retrieve = AsyncMock(side_effect=RuntimeError("not found"))
    fake_client.close = AsyncMock()

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(rl_trainer_module, "AsyncTogether", fake_together)

    with pytest.raises(RuntimeError, match="not found"):
        await Trainer.attach_async(session_id="missing")

    fake_client.close.assert_awaited_once()


async def test_detach_async_closes_client_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock()
    client.close = AsyncMock()
    trainer = Trainer("sess", _client=cast(Any, client))

    await trainer.detach_async()

    client.close.assert_awaited_once()
    client.beta.rl.sessions.stop.assert_not_awaited()


def test_detach_closes_event_loop_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock()
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    trainer = Trainer("sess", _client=cast(Any, client))
    trainer._event_loop = event_loop

    trainer.detach()

    assert event_loop.is_closed()
    assert trainer._event_loop is None
    client.close.assert_awaited_once()
    client.beta.rl.sessions.stop.assert_not_awaited()


async def test_submit_and_wait_raises_on_empty_output(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_wait(*_args: Any, **_kwargs: Any) -> Any:  # noqa: ARG001
        return SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_COMPLETED", output=None)

    monkeypatch.setattr(rl_ops, "async_wait_for_operation", fake_wait)
    trainer = _make_trainer()

    op = SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING")
    with pytest.raises(RuntimeError, match="empty output"):
        await trainer._submit_and_wait(op, timeout=10.0, interval=0.1)


def _small_sample() -> Sample:
    return Sample(
        model_input=SampleModelInput(
            chunks=[
                SampleModelInputChunk(
                    encoded_text=SampleModelInputChunkEncodedText(tokens=[1, 2, 3]),
                )
            ],
        ),
        loss_inputs=LossInputsParam(
            target_tokens=LossTargetTokensParam(data=[1, 2, 3], dtype="D_TYPE_INT64"),
            loss_mask=LossMaskParam(
                data=[1, 0, 1],
                dtype="D_TYPE_INT64",
            ),
        ),
    )


def test_forward_backward_inline_below_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    """Small payloads are sent inline without triggering upload."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_trainer(client)

    result = trainer.forward_backward(
        samples=[_small_sample()],
        loss=LossConfigParam(type="LOSS_TYPE_CROSS_ENTROPY"),
    )

    assert result.loss == 0.5
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs.get("extra_body") is None
    assert kwargs["samples"] == [_small_sample()]
    trainer.stop()


async def test_forward_backward_uploads_large_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding the threshold are uploaded; inline samples have truncated sequences."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=2.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    client = FakeClient()
    trainer = _make_trainer(client)

    long_tokens = list(range(20))
    long_mask = [1] * 20
    sample = Sample(
        model_input=SampleModelInput(
            chunks=[
                SampleModelInputChunk(
                    encoded_text=SampleModelInputChunkEncodedText(tokens=long_tokens),
                )
            ],
        ),
        loss_inputs=LossInputsParam(
            target_tokens=LossTargetTokensParam(data=long_tokens, dtype="D_TYPE_INT64"),
            loss_mask=LossMaskParam(
                data=long_mask,
                dtype="D_TYPE_INT64",
            ),
        ),
    )

    result = await trainer.forward_backward_async(
        samples=[sample],
        loss=LossConfigParam(type="LOSS_TYPE_CROSS_ENTROPY"),
    )

    assert result.loss == 2.0

    # Full payload is uploaded to R2
    assert client.captured_put_body is not None
    uploaded = json.loads(client.captured_put_body)
    assert uploaded["samples"][0]["model_input"]["chunks"][0]["encoded_text"]["tokens"] == long_tokens

    # Inline request carries all samples with truncated sequences
    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["extra_body"] == {"payload_id": "pid-123"}
    assert len(kwargs["samples"]) == 1
    sent = kwargs["samples"][0]
    assert sent["model_input"]["chunks"][0]["encoded_text"]["tokens"] == long_tokens[:8]
    assert sent["loss_inputs"]["loss_mask"]["data"] == long_mask[:8]


def test_forward_backward_rejects_payload_above_max(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding R2's single-PUT limit raise before any upload is attempted."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    monkeypatch.setattr(rl_payloads_module, "_MAX_PAYLOAD_SIZE", 20)
    client = FakeClient()
    trainer = _make_trainer(client)

    with pytest.raises(ValueError, match="exceeds"):
        trainer.forward_backward(
            samples=[
                Sample(
                    model_input=SampleModelInput(
                        chunks=[
                            SampleModelInputChunk(
                                encoded_text=SampleModelInputChunkEncodedText(tokens=list(range(50))),
                            )
                        ],
                    ),
                    loss_inputs=LossInputsParam(
                        target_tokens=LossTargetTokensParam(data=list(range(50)), dtype="D_TYPE_INT64"),
                        loss_mask=LossMaskParam(data=[1] * 50, dtype="D_TYPE_INT64"),
                    ),
                )
            ],
            loss=LossConfigParam(type="LOSS_TYPE_CROSS_ENTROPY"),
        )

    assert client.captured_put_body is None
    trainer.stop()
