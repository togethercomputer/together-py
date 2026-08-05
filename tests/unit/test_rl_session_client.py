from __future__ import annotations

import json
import asyncio
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from together.lib.beta.rl import (
    Sample,
    Logprob,
    Weights,
    Gradient,
    AdamParams,
    LoraConfig,
    LossConfig,
    LossInputs,
    ModelInput,
    MuonParams,
    SampleResult,
    ForwardResult,
    SessionClient,
    WandbMetadata,
    SamplingClient,
    TrainingClient,
    ModelInputChunk,
    OptimStepResult,
    SessionMetadata,
    EncodedTextChunk,
    LossTargetTokens,
    WeightsSyncResult,
    ForwardBackwardResult,
    TrainingCheckpointResult,
    InferenceCheckpointResult,
    _payloads as rl_payloads_module,
    _operations as rl_ops,
)
from together.lib.beta.rl.clients import (
    session as session_client_module,
    sampling as sampling_client_module,
    training as training_client_module,
)
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
        self.status_value: str | None = "TRAINING_SESSION_STATUS_RUNNING"

    async def stop(self, session_id: str) -> dict[str, Any]:
        self.last_stop = session_id
        return {"id": "stop-op"}

    async def retrieve(self, _session_id: str) -> Any:
        return SimpleNamespace(
            status=self.status_value,
            resources_id="res-1",
        )


class FakeModelResources:
    def __init__(self, num_generator_replicas: int = 1) -> None:
        self.num_generator_replicas = num_generator_replicas

    async def retrieve(self, _model_resources_id: str) -> Any:
        return SimpleNamespace(
            compute_config=SimpleNamespace(
                num_generator_replicas=self.num_generator_replicas,
            )
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


def _make_session(client: FakeClient | None = None) -> SessionClient:
    if client is None:
        client = FakeClient()
    return SessionClient("sess", _client=cast(Any, client))


def _sample_payload(sample: Sample) -> dict[str, Any]:
    return dict(sample)


def _sampling(session: SessionClient) -> SamplingClient:
    sampling = session.sampling
    assert sampling is not None
    return sampling


def _patch_submit_and_wait(monkeypatch: pytest.MonkeyPatch, result: Any) -> None:
    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        return result

    monkeypatch.setattr(SessionClient, "_submit_and_wait", fake)


def test_session_exposes_capability_clients() -> None:
    session = _make_session()

    assert isinstance(session.training, TrainingClient)
    assert isinstance(session.sampling, SamplingClient)
    assert session.training.session_id == session.session_id
    sampling = session.sampling
    assert sampling is not None
    assert sampling.session_id == session.session_id


def test_lora_config_has_clean_public_name() -> None:
    assert LoraConfig(rank=8) == {"rank": 8}


def test_trainer_only_session_rejects_sampling_access() -> None:
    session = SessionClient("sess", _client=cast(Any, FakeClient()), _has_sampling=False)

    assert session.has_sampling is False
    with pytest.raises(RuntimeError, match="does not have sampling capability"):
        _ = session.sampling


def test_sample_wraps_model_input(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = SampleResult(policy_segments=[], sequences=[])
    _patch_submit_and_wait(monkeypatch, SimpleNamespace(results=[expected]))
    client = FakeClient()
    trainer = _make_session(client)

    model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[101, 102]))])
    result = _sampling(trainer).sample(prompt=model_input, num_samples=3)

    assert result is expected
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["model_inputs"] == [model_input]
    trainer.stop()


def test_sample_batch_passes_multiple_model_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = [
        SampleResult(policy_segments=[], sequences=[]),
        SampleResult(policy_segments=[], sequences=[]),
    ]
    _patch_submit_and_wait(monkeypatch, SimpleNamespace(results=expected))
    client = FakeClient()
    trainer = _make_session(client)

    model_inputs = [
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))]),
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[3, 4]))]),
    ]
    result = _sampling(trainer).sample_batch(prompts=model_inputs)

    assert result == expected
    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["model_inputs"] == model_inputs
    trainer.stop()


def test_compute_logprobs_requests_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SampleResult(policy_segments=[], sequences=[], prompt_logprobs=[0.0, -1.5])
    _patch_submit_and_wait(monkeypatch, SimpleNamespace(results=[result]))
    client = FakeClient()
    trainer = _make_session(client)

    model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))])
    logprobs = _sampling(trainer).compute_logprobs(model_input)

    assert logprobs == [0.0, -1.5]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["model_inputs"] == [model_input]
    assert kwargs["num_samples"] == 1
    assert kwargs["prompt_logprobs"] is True
    assert kwargs["sampling_params"]["max_tokens"] == 1
    trainer.stop()


def test_compute_logprobs_batch_requests_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    results = [
        SampleResult(policy_segments=[], sequences=[], prompt_logprobs=[0.0, -1.5]),
        SampleResult(policy_segments=[], sequences=[], prompt_logprobs=[0.0, -0.2]),
    ]
    _patch_submit_and_wait(monkeypatch, SimpleNamespace(results=results))
    client = FakeClient()
    trainer = _make_session(client)

    model_inputs = [
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))]),
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[3, 4]))]),
    ]
    logprobs = _sampling(trainer).compute_logprobs_batch(model_inputs)

    assert logprobs == [[0.0, -1.5], [0.0, -0.2]]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "sample"
    assert args == ("sess",)
    assert kwargs["model_inputs"] == model_inputs
    assert kwargs["num_samples"] == 1
    assert kwargs["prompt_logprobs"] is True
    assert kwargs["sampling_params"]["max_tokens"] == 1
    trainer.stop()


def test_prompt_logprobs_from_results_raises_when_missing() -> None:
    result = SampleResult(policy_segments=[], sequences=[])
    with pytest.raises(RuntimeError, match="prompt logprobs"):
        sampling_client_module._prompt_logprobs_from_results([result])


def test_forward_passes_samples(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(
        monkeypatch,
        ForwardResult(logprobs=[Logprob(data=[-1.0, -2.0, -3.0])]),
    )
    client = FakeClient()
    trainer = _make_session(client)

    samples = [_small_sample()]
    result = trainer.training.forward(samples=samples)

    assert result.logprobs[0].data == [-1.0, -2.0, -3.0]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs.get("extra_body") is None
    trainer.stop()


def test_custom_forward_backward_passes_samples_and_gradients(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, {"metrics": {"grad_norm": 0.5}})
    client = FakeClient()
    trainer = _make_session(client)

    samples = [_small_sample()]
    gradients = [Gradient(data=[0.1, -0.2, 0.3], dtype="D_TYPE_FLOAT32")]
    result = trainer.training.custom_forward_backward(samples=samples, gradients=gradients)

    assert result == {"metrics": {"grad_norm": 0.5}}
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "custom_forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs["gradients"] == gradients
    assert kwargs.get("extra_body") is None
    trainer.stop()


def test_forward_backward_passes_samples_and_loss(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    samples = [
        Sample(
            model_input=ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))]),
            loss_inputs=LossInputs(
                target_tokens=LossTargetTokens(data=[1, 2, 3], dtype="D_TYPE_INT64"),
                weights=Weights(
                    data=[1.0, 0.0, 1.0],
                    dtype="D_TYPE_FLOAT32",
                ),
            ),
        )
    ]
    loss = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")

    result = trainer.training.forward_backward(samples=samples, loss=loss)

    assert result.loss == 1.0
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs["loss"] == loss
    trainer.stop()


def test_optim_step_passes_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.training.optim_step(
        adam_params=AdamParams(beta1=0.9, learning_rate=1e-4, grad_clip_norm=1.0),
    )

    assert result.step == "1"
    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["adam_params"] == {"beta1": 0.9, "learning_rate": 1e-4, "grad_clip_norm": 1.0}
    trainer.stop()


def test_optim_step_forwards_muon_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.training.optim_step(
        muon_params=MuonParams(learning_rate=0.02, momentum=0.95),
    )

    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["muon_params"] == {"learning_rate": 0.02, "momentum": 0.95}
    trainer.stop()


def test_weights_sync_passes_params(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, WeightsSyncResult(weights_version=2))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.training.weights_sync(weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")

    assert result.weights_version == 2
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "weights_sync"
    assert args == ("sess",)
    assert kwargs["weight_sync_type"] == "WEIGHT_SYNC_TYPE_SYNCHRONOUS"
    trainer.stop()


def test_create_training_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_submit_and_wait(monkeypatch, TrainingCheckpointResult(checkpoint_id="ckpt-1"))
    client = FakeClient()
    trainer = _make_session(client)

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
    trainer = _make_session(client)

    result = trainer.create_inference_checkpoint()

    assert result.registered_model_name == "model-1"
    trainer.stop()


def test_retrieve_returns_session() -> None:
    client = FakeClient()
    trainer = _make_session(client)

    session = trainer.retrieve()

    assert session.status == "TRAINING_SESSION_STATUS_RUNNING"
    trainer.stop()


async def test_retrieve_async_returns_session() -> None:
    client = FakeClient()
    trainer = _make_session(client)

    session = await trainer.retrieve_async()

    assert session.status == "TRAINING_SESSION_STATUS_RUNNING"
    await trainer.stop_async()


def test_stop_closes_client() -> None:
    client = FakeClient()
    trainer = _make_session(client)

    trainer.stop()

    assert client.beta.rl.sessions.last_stop == "sess"
    assert client.closed is True


def test_context_manager_stops() -> None:
    client = FakeClient()
    trainer = _make_session(client)

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
    fake_client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(
            compute_config=SimpleNamespace(num_generator_replicas=1),
        )
    )
    create_client = MagicMock(return_value=fake_client)
    monkeypatch.setattr(session_client_module, "AsyncTogether", create_client)

    trainer = await SessionClient.create_async(
        model_resources_id="res-1",
        api_key="api-key",
        base_url="http://127.0.0.1:4010",
        display_name="my-run",
        metadata=SessionMetadata(wandb=WandbMetadata(project="proj", run_id="run-1")),
        lora_config=LoraConfig(rank=8, alpha=16, dropout=0.1),
        timeout=0.1,
        interval=0.0,
    )

    assert trainer._session_id == "sess-1"
    assert isinstance(trainer.sampling, SamplingClient)
    assert create_client.call_args.kwargs["max_retries"] == 7
    fake_client.beta.rl.sessions.retrieve.assert_awaited_once_with("sess-1")
    await_args = fake_client.beta.rl.sessions.create.await_args
    assert await_args is not None
    create_kwargs = await_args.kwargs
    assert create_kwargs["model_resources_id"] == "res-1"
    assert create_kwargs["display_name"] == "my-run"
    assert create_kwargs["metadata"] == {"wandb": {"project": "proj", "run_id": "run-1"}}
    assert create_kwargs["lora_config"] == {"rank": 8, "alpha": 16, "dropout": 0.1}


async def test_create_async_closes_client_on_terminal_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.create = AsyncMock(return_value=SimpleNamespace(id="sess-1"))
    fake_client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_ERROR")
    )
    fake_client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(
            compute_config=SimpleNamespace(num_generator_replicas=1),
        )
    )
    fake_client.close = AsyncMock()

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(session_client_module, "AsyncTogether", fake_together)

    with pytest.raises(RuntimeError, match="TRAINING_SESSION_STATUS_ERROR"):
        await SessionClient.create_async(
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
    trainer = SessionClient("sess", _client=cast(Any, client))

    with pytest.raises(RuntimeError, match=status):
        await trainer._wait_for_creation_async(timeout=1.0, interval=0.0)


async def test_wait_for_creation_times_out() -> None:
    client = MagicMock()
    client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_CREATING")
    )
    trainer = SessionClient("sess", _client=cast(Any, client))

    with pytest.raises(TimeoutError):
        await trainer._wait_for_creation_async(timeout=0.0, interval=0.0)


async def test_stop_async_closes_client_and_event_loop() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value={"id": "stop-op"})
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    trainer = SessionClient("sess", _client=cast(Any, client))
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
        return_value=SimpleNamespace(
            status="TRAINING_SESSION_STATUS_RUNNING",
            resources_id="res-1",
        )
    )
    fake_client.beta.rl.model_resources.retrieve = AsyncMock(
        return_value=SimpleNamespace(
            compute_config=SimpleNamespace(num_generator_replicas=1),
        )
    )
    fake_client.close = AsyncMock()
    create_client = MagicMock(return_value=fake_client)
    monkeypatch.setattr(session_client_module, "AsyncTogether", create_client)

    trainer = await SessionClient.attach_async(session_id="sess-1")

    assert trainer._session_id == "sess-1"
    assert isinstance(trainer.sampling, SamplingClient)
    assert create_client.call_args.kwargs["max_retries"] == 7
    fake_client.beta.rl.sessions.retrieve.assert_awaited_once_with("sess-1")
    fake_client.beta.rl.sessions.create.assert_not_awaited()
    fake_client.close.assert_not_awaited()


async def test_attach_async_hides_sampling_for_trainer_only_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = FakeClient()
    fake_client.beta.rl.model_resources.num_generator_replicas = 0

    def fake_together(**_kwargs: Any) -> FakeClient:
        return fake_client

    monkeypatch.setattr(session_client_module, "AsyncTogether", fake_together)

    session = await SessionClient.attach_async(session_id="sess-1")

    assert session.has_sampling is False
    with pytest.raises(RuntimeError, match="does not have sampling capability"):
        _ = session.sampling


async def test_attach_async_raises_and_closes_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_client = MagicMock()
    fake_client.beta.rl.sessions.retrieve = AsyncMock(side_effect=RuntimeError("not found"))
    fake_client.close = AsyncMock()

    def fake_together(**_kw: Any) -> MagicMock:
        return fake_client

    monkeypatch.setattr(session_client_module, "AsyncTogether", fake_together)

    with pytest.raises(RuntimeError, match="not found"):
        await SessionClient.attach_async(session_id="missing")

    fake_client.close.assert_awaited_once()


async def test_detach_async_closes_client_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock()
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    await trainer.detach_async()

    client.close.assert_awaited_once()
    client.beta.rl.sessions.stop.assert_not_awaited()


def test_detach_closes_event_loop_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock()
    client.close = AsyncMock()
    event_loop = asyncio.new_event_loop()
    trainer = SessionClient("sess", _client=cast(Any, client))
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
    trainer = _make_session()

    op = SampleOperation(id="op-1", status="TRAINING_OPERATION_STATUS_PENDING")
    with pytest.raises(RuntimeError, match="empty output"):
        await trainer._submit_and_wait(op, timeout=10.0, interval=0.1)


def _small_sample() -> Sample:
    return Sample(
        model_input=ModelInput(
            chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))],
        ),
        loss_inputs=LossInputs(
            target_tokens=LossTargetTokens(data=[1, 2, 3], dtype="D_TYPE_INT64"),
            weights=Weights(
                data=[1.0, 0.0, 1.0],
                dtype="D_TYPE_FLOAT32",
            ),
        ),
    )


def test_forward_backward_inline_below_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    """Small payloads are sent inline without triggering upload."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.training.forward_backward(
        samples=[_small_sample()],
        loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
    )

    assert result.loss == 0.5
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs.get("extra_body") is None
    assert kwargs["samples"] == [_sample_payload(_small_sample())]
    trainer.stop()


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("ppo", "LOSS_TYPE_PPO"),
        ("cross_entropy", "LOSS_TYPE_CROSS_ENTROPY"),
        ("LOSS_TYPE_PPO", "LOSS_TYPE_PPO"),
    ],
)
def test_resolve_loss_type(given: str, expected: str) -> None:
    loss = cast(Any, {"type": given, "grpo_params": {"beta": 0.1}})

    assert training_client_module._resolve_loss_type(loss) == {"type": expected, "grpo_params": {"beta": 0.1}}
    assert loss["type"] == given, "input config must not be mutated"


def test_resolve_loss_type_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unknown loss type"):
        training_client_module._resolve_loss_type(cast(Any, {"type": "gspo"}))


def test_forward_backward_sends_proto_loss_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Short loss names reach the API in their proto spelling."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.training.forward_backward(samples=[_small_sample()], loss=cast(Any, {"type": "ppo"}))

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["loss"] == {"type": "LOSS_TYPE_PPO"}
    trainer.stop()


async def test_forward_backward_uploads_large_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding the threshold are uploaded; inline samples have truncated sequences."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=2.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    client = FakeClient()
    trainer = _make_session(client)

    long_tokens = list(range(20))
    long_weights = [1.0] * 20
    sample = Sample(
        model_input=ModelInput(
            chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=long_tokens))],
        ),
        loss_inputs=LossInputs(
            target_tokens=LossTargetTokens(data=long_tokens, dtype="D_TYPE_INT64"),
            weights=Weights(
                data=long_weights,
                dtype="D_TYPE_FLOAT32",
            ),
        ),
    )

    result = await trainer.training.forward_backward_async(
        samples=[sample],
        loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
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
    assert sent["loss_inputs"]["weights"]["data"] == long_weights[:8]


def test_forward_backward_rejects_payload_above_max(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding R2's single-PUT limit raise before any upload is attempted."""
    _patch_submit_and_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    monkeypatch.setattr(rl_payloads_module, "_MAX_PAYLOAD_SIZE", 20)
    client = FakeClient()
    trainer = _make_session(client)

    with pytest.raises(ValueError, match="exceeds"):
        trainer.training.forward_backward(
            samples=[
                Sample(
                    model_input=ModelInput(
                        chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=list(range(50))))],
                    ),
                    loss_inputs=LossInputs(
                        target_tokens=LossTargetTokens(data=list(range(50)), dtype="D_TYPE_INT64"),
                        weights=Weights(data=[1.0] * 50, dtype="D_TYPE_FLOAT32"),
                    ),
                )
            ],
            loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
        )

    assert client.captured_put_body is None
    trainer.stop()
