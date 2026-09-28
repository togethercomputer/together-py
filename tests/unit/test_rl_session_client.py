from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from together import NotFoundError, omit
from tests.unit.rl_wait import patch_wait
from tests.unit._rl_fakes import FakeClient
from together.lib.beta.rl import (
    Sample,
    Trainer,
    Gradient,
    Generator,
    AdamParams,
    LoraConfig,
    LossConfig,
    ModelInput,
    MuonParams,
    TensorData,
    SampleResult,
    SessionClient,
    WandbMetadata,
    ModelInputChunk,
    OptimStepResult,
    SessionMetadata,
    EncodedTextChunk,
    WeightsSyncResult,
    ForwardBackwardResult,
    TrainingCheckpointResult,
    InferenceCheckpointResult,
    _losses as rl_losses,
    _payloads as rl_payloads_module,
    _operations as rl_ops,
)
from together.lib.beta.rl.clients import (
    session as session_client_module,
    trainer as trainer_module,
    generator as generator_module,
)
from together.types.beta.rl.tensor_data import TensorData as TensorDataModel
from together.types.beta.rl.loss_fn_output import LossFnOutput
from together.types.beta.rl.sample_operation import SampleOperation


def _make_session(client: FakeClient | None = None) -> SessionClient:
    if client is None:
        client = FakeClient()
    return SessionClient("sess", _client=cast(Any, client))


def _sample_payload(sample: Sample) -> dict[str, Any]:
    return dict(sample)


_CROSS_ENTROPY = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")


def _scored_result(*logprobs: list[float]) -> ForwardBackwardResult:
    """A forward_only result, whose per-sample outputs carry the logprobs forward reads."""
    return ForwardBackwardResult(
        loss=0.5,
        loss_fn_outputs=[
            LossFnOutput(tensors={"logprobs": TensorDataModel(data=values, dtype="float32")}) for values in logprobs
        ],
    )


def _generator(session: SessionClient) -> Generator:
    generator = session.generator
    assert generator is not None
    return generator


def test_session_exposes_capability_clients() -> None:
    session = _make_session()

    assert isinstance(session.trainer, Trainer)
    assert isinstance(session.generator, Generator)
    assert session.trainer.session_id == session.session_id
    generator = session.generator
    assert generator is not None
    assert generator.session_id == session.session_id


def test_lora_config_has_clean_public_name() -> None:
    assert LoraConfig(rank=8) == {"rank": 8}


def test_trainer_only_session_rejects_generator_access() -> None:
    session = SessionClient("sess", _client=cast(Any, FakeClient()), _has_generator=False)

    assert session.has_generator is False
    with pytest.raises(RuntimeError, match="does not have generator capability"):
        _ = session.generator


def test_sample_wraps_model_input(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = SampleResult(policy_segments=[], sequences=[])
    patch_wait(monkeypatch, SimpleNamespace(results=[expected]))
    client = FakeClient()
    trainer = _make_session(client)

    model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[101, 102]))])
    result = _generator(trainer).sample(prompt=model_input, num_samples=3)

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
    patch_wait(monkeypatch, SimpleNamespace(results=expected))
    client = FakeClient()
    trainer = _make_session(client)

    model_inputs = [
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))]),
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[3, 4]))]),
    ]
    result = _generator(trainer).sample_batch(prompts=model_inputs)

    assert result == expected
    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["model_inputs"] == model_inputs
    trainer.stop()


def test_sample_requests_routing_capture(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = SampleResult(policy_segments=[], sequences=[])
    patch_wait(monkeypatch, SimpleNamespace(results=[expected]))
    client = FakeClient()
    trainer = _make_session(client)
    model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))])

    result = _generator(trainer).sample(
        prompt=model_input,
        return_routed_experts=True,
        topk_prompt_logprobs=5,
    )

    assert result is expected
    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["return_routed_experts"] is True
    assert kwargs["topk_prompt_logprobs"] == 5
    trainer.stop()


def test_compute_logprobs_requests_prompt_logprobs(monkeypatch: pytest.MonkeyPatch) -> None:
    result = SampleResult(policy_segments=[], sequences=[], prompt_logprobs=[0.0, -1.5])
    patch_wait(monkeypatch, SimpleNamespace(results=[result]))
    client = FakeClient()
    trainer = _make_session(client)

    model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))])
    logprobs = _generator(trainer).compute_logprobs(model_input)

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
    patch_wait(monkeypatch, SimpleNamespace(results=results))
    client = FakeClient()
    trainer = _make_session(client)

    model_inputs = [
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2]))]),
        ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[3, 4]))]),
    ]
    logprobs = _generator(trainer).compute_logprobs_batch(model_inputs)

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
        generator_module._prompt_logprobs_from_results([result])


def test_forward_scores_the_batch_without_gradients(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, _scored_result([-1.0, -2.0, -3.0]))
    client = FakeClient()
    trainer = _make_session(client)

    samples = [_small_sample()]
    result = trainer.trainer.forward(samples=samples, loss=_CROSS_ENTROPY)

    assert result.loss_fn_outputs is not None
    assert result.loss_fn_outputs[0].tensors["logprobs"].data == [-1.0, -2.0, -3.0]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs["loss"] == _CROSS_ENTROPY
    assert kwargs["forward_only"] is True
    assert kwargs["return_loss_fn_outputs"] is True
    assert kwargs.get("extra_body") is None
    trainer.stop()


def test_forward_backward_accumulates_gradients(monkeypatch: pytest.MonkeyPatch) -> None:
    """The gradient path must send neither flag, leaving the service defaults in force."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.trainer.forward_backward(samples=[_small_sample()], loss=_CROSS_ENTROPY)

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["forward_only"] is omit
    assert kwargs["return_loss_fn_outputs"] is omit
    trainer.stop()


def test_custom_forward_backward_passes_samples_and_gradients(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, {"metrics": {"grad_norm": 0.5}})
    client = FakeClient()
    trainer = _make_session(client)

    samples = [_small_sample()]
    gradients = [Gradient(data=[0.1, -0.2, 0.3], dtype="D_TYPE_FLOAT32")]
    result = trainer.trainer.custom_forward_backward(samples=samples, gradients=gradients)

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
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    samples = [
        Sample(
            model_input=ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))]),
            loss_fn_inputs={
                "target_tokens": TensorData(data=[1, 2, 3], dtype="int64"),
                "weights": TensorData(
                    data=[1.0, 0.0, 1.0],
                    dtype="float32",
                ),
            },
        )
    ]
    loss = LossConfig(type="LOSS_TYPE_CROSS_ENTROPY")

    result = trainer.trainer.forward_backward(samples=samples, loss=loss)

    assert result.loss == 1.0
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward_backward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs["loss"] == loss
    trainer.stop()


def test_optim_step_passes_params(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.trainer.optim_step(
        adam_params=AdamParams(beta1=0.9, learning_rate=1e-4, grad_clip_norm=1.0),
    )

    assert result.step == "1"
    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["adam_params"] == {"beta1": 0.9, "learning_rate": 1e-4, "grad_clip_norm": 1.0}
    trainer.stop()


def test_optim_step_forwards_muon_params(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, OptimStepResult(step="1"))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.trainer.optim_step(
        muon_params=MuonParams(learning_rate=0.02, momentum=0.95),
    )

    assert client.beta.rl.operations.last_call is not None
    method, _, kwargs = client.beta.rl.operations.last_call
    assert method == "optim_step"
    assert kwargs["muon_params"] == {"learning_rate": 0.02, "momentum": 0.95}
    trainer.stop()


def test_weights_sync_passes_params(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, WeightsSyncResult(weights_version=2))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.trainer.weights_sync()

    assert int(result.weights_version) == 2
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "weights_sync"
    assert args == ("sess",)
    assert kwargs["weight_sync_type"] == "WEIGHT_SYNC_TYPE_SYNCHRONOUS"
    trainer.stop()


def test_create_training_checkpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(monkeypatch, TrainingCheckpointResult(checkpoint_id="ckpt-1"))
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
    patch_wait(monkeypatch, InferenceCheckpointResult(model_name="model-1"))
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


async def test_async_context_manager_stops() -> None:
    client = FakeClient()
    trainer = _make_session(client)

    async with trainer:
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
    assert isinstance(trainer.generator, Generator)
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


def _instant_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(session_client_module, "DEFAULT_SESSION_STOP_TIMEOUT", 0.0)
    monkeypatch.setattr(session_client_module, "DEFAULT_SESSION_STOP_INTERVAL", 0.0)


async def test_stop_async_closes_client() -> None:
    client = MagicMock()
    output = SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPED")
    client.beta.rl.sessions.stop = AsyncMock(return_value=output)
    client.beta.rl.sessions.retrieve = AsyncMock()
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    result = await trainer.stop_async()

    assert result is output
    assert trainer._loop.closed
    client.beta.rl.sessions.stop.assert_awaited_once_with("sess")
    client.beta.rl.sessions.retrieve.assert_not_awaited()
    client.close.assert_awaited_once()


async def test_stop_async_waits_until_session_is_inactive(monkeypatch: pytest.MonkeyPatch) -> None:
    _instant_stop(monkeypatch)
    client = MagicMock()
    output = SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPING")
    client.beta.rl.sessions.stop = AsyncMock(return_value=output)
    client.beta.rl.sessions.retrieve = AsyncMock(return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPED"))
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    result = await trainer.stop_async()

    assert result is output
    client.beta.rl.sessions.retrieve.assert_awaited_once_with("sess")
    client.close.assert_awaited_once()


async def test_stop_async_treats_missing_session_as_inactive(monkeypatch: pytest.MonkeyPatch) -> None:
    _instant_stop(monkeypatch)
    request = httpx.Request("GET", "https://api.together.xyz/sessions/sess")
    not_found = NotFoundError(
        "Session not found",
        response=httpx.Response(404, request=request),
        body=None,
    )
    client = MagicMock()
    output = SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPING")
    client.beta.rl.sessions.stop = AsyncMock(return_value=output)
    client.beta.rl.sessions.retrieve = AsyncMock(side_effect=not_found)
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    result = await trainer.stop_async()

    assert result is output
    client.close.assert_awaited_once()


async def test_stop_async_warns_on_timeout_and_closes_client(monkeypatch: pytest.MonkeyPatch) -> None:
    _instant_stop(monkeypatch)
    client = MagicMock()
    output = SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPING")
    client.beta.rl.sessions.stop = AsyncMock(return_value=output)
    client.beta.rl.sessions.retrieve = AsyncMock(
        return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPING")
    )
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    with pytest.warns(UserWarning, match="model_resources.stop\\(force=True\\)"):
        result = await trainer.stop_async()

    assert result is output
    client.close.assert_awaited_once()


async def test_stop_async_does_not_swallow_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch) -> None:
    _instant_stop(monkeypatch)
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPING"))
    client.beta.rl.sessions.retrieve = AsyncMock(side_effect=KeyboardInterrupt)
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    with pytest.raises(KeyboardInterrupt):
        await trainer._stop_remote()

    client.close.assert_not_awaited()


def test_stop_marks_the_handle_closed() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value=SimpleNamespace(status="TRAINING_SESSION_STATUS_STOPPED"))
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))
    trainer.stop()

    assert trainer._loop.closed


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
    assert isinstance(trainer.generator, Generator)
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

    assert session.has_generator is False
    with pytest.raises(RuntimeError, match="does not have generator capability"):
        _ = session.generator


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


def test_detach_marks_the_handle_closed_without_stopping() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock()
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))
    trainer.detach()

    assert trainer._loop.closed
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
        loss_fn_inputs={
            "target_tokens": TensorData(data=[1, 2, 3], dtype="int64"),
            "weights": TensorData(
                data=[1.0, 0.0, 1.0],
                dtype="float32",
            ),
        },
    )


def _policy_sample(*, reference_logprobs: bool = False) -> Sample:
    inputs: dict[str, Any] = {
        "target_tokens": TensorData(data=[1, 2, 3], dtype="int64"),
        "logprobs": TensorData(data=[-0.1, -0.2, -0.3], dtype="float32"),
        "advantages": TensorData(data=[1.0, 0.5, -0.5], dtype="float32"),
    }
    if reference_logprobs:
        inputs["reference_logprobs"] = TensorData(data=[-0.2, -0.3, -0.4], dtype="float32")
    return Sample(
        model_input=ModelInput(
            chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))],
        ),
        loss_fn_inputs=inputs,
    )


def test_forward_backward_inline_below_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    """Small payloads are sent inline without triggering upload."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    result = trainer.trainer.forward_backward(
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


def test_forward_backward_materializes_generator_weights(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nested Iterable[float] fields must survive transform on the small path."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    sample = Sample(
        model_input=ModelInput(
            chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))],
        ),
        loss_fn_inputs={
            "target_tokens": TensorData(data=[1, 2, 3], dtype="int64"),
            "weights": TensorData(
                data=(value for value in (1.0, 0.0, 1.0)),
                dtype="float32",
            ),
        },
    )
    trainer.trainer.forward_backward(
        samples=[sample],
        loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
    )

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["samples"][0]["loss_fn_inputs"]["weights"]["data"] == [1.0, 0.0, 1.0]
    trainer.stop()


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("ppo", "LOSS_TYPE_PPO"),
        ("dppo", "LOSS_TYPE_DPPO"),
        ("cross_entropy", "LOSS_TYPE_CROSS_ENTROPY"),
        ("LOSS_TYPE_PPO", "LOSS_TYPE_PPO"),
    ],
)
def test_resolve_loss_type(given: str, expected: str) -> None:
    loss = cast(Any, {"type": given, "grpo_params": {"beta": 0.1}})

    assert trainer_module._resolve_loss_type(loss) == {"type": expected, "grpo_params": {"beta": 0.1}}
    assert loss["type"] == given, "input config must not be mutated"


def test_resolve_loss_type_passes_unknown_name_through() -> None:
    """Normalizing is not validating: `_losses` owns the one loss-type vocabulary.

    An unrecognized name reaches `validate_loss_config` untouched so a caller sees one
    error naming one set of accepted types, not two with different alphabets.
    """
    assert trainer_module._resolve_loss_type(cast(Any, {"type": "gspo"})) == {"type": "gspo"}

    with pytest.raises(ValueError, match="Unsupported loss type"):
        rl_losses.validate_loss_config(cast(Any, {"type": "gspo"}))


def test_forward_backward_sends_proto_loss_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Short loss names reach the API in their proto spelling."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.trainer.forward_backward(samples=[_policy_sample()], loss=cast(Any, {"type": "ppo"}))

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["loss"] == {"type": "LOSS_TYPE_PPO"}
    trainer.stop()


@pytest.mark.parametrize(
    ("loss", "sample"),
    [
        ({"type": "LOSS_TYPE_CROSS_ENTROPY"}, _small_sample()),
        ({"type": "LOSS_TYPE_GRPO", "grpo_params": {"beta": 0.1}}, _policy_sample(reference_logprobs=True)),
        ({"type": "LOSS_TYPE_IMPORTANCE_SAMPLING"}, _policy_sample()),
        ({"type": "LOSS_TYPE_PPO", "ppo_params": {"clip_low_threshold": 0.8}}, _policy_sample()),
        ({"type": "LOSS_TYPE_CISPO", "cispo_params": {"clip_high_threshold": 1.2}}, _policy_sample()),
        ({"type": "LOSS_TYPE_DRO", "dro_params": {"beta": 0.1}}, _policy_sample()),
        ({"type": "LOSS_TYPE_DPPO"}, _policy_sample()),
        ({"type": "LOSS_TYPE_DPPO", "dppo_params": {}}, _policy_sample()),
        ({"type": "LOSS_TYPE_DPPO", "dppo_params": {"delta_low": 0.1, "delta_high": 0.2}}, _policy_sample()),
    ],
)
def test_forward_backward_accepts_each_generated_loss(
    monkeypatch: pytest.MonkeyPatch,
    loss: dict[str, Any],
    sample: Sample,
) -> None:
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    session = _make_session(client)

    session.trainer.forward_backward(samples=(item for item in [sample]), loss=cast(Any, loss))

    assert client.beta.rl.operations.last_call is not None
    assert client.beta.rl.operations.last_call[2]["loss"] == loss
    session.stop()


@pytest.mark.parametrize(
    ("loss", "message"),
    [
        ({}, "Unsupported loss type"),
        ({"type": "LOSS_TYPE_DRO"}, "dro_params"),
        ({"type": "LOSS_TYPE_DRO", "dro_params": {}}, "beta"),
        ({"type": "LOSS_TYPE_PPO", "ppo_params": {"beta": 0.1}}, "Unsupported keys"),
        ({"type": "LOSS_TYPE_PPO", "grpo_params": {}}, "Unsupported keys"),
        ({"type": "LOSS_TYPE_DPPO", "dppo_params": {"beta": 0.1}}, "Unsupported keys"),
        ({"type": "LOSS_TYPE_DPPO", "ppo_params": {}}, "Unsupported keys"),
        ({"type": "LOSS_TYPE_PPO", "dppo_params": {}}, "Unsupported keys"),
    ],
)
def test_forward_backward_rejects_invalid_loss_config_before_submission(
    loss: dict[str, Any],
    message: str,
) -> None:
    client = FakeClient()
    session = _make_session(client)

    with pytest.raises(ValueError, match=message):
        session.trainer.forward_backward(samples=[_policy_sample()], loss=cast(Any, loss))

    assert client.beta.rl.operations.last_call is None
    assert client.captured_put_body is None
    session.stop()


@pytest.mark.parametrize(
    ("method", "sample", "message"),
    [
        ("forward_backward", _small_sample(), "advantages"),
        (
            "forward",
            cast(
                Any,
                {
                    "model_input": ModelInput(
                        chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))]
                    ),
                    "loss_fn_inputs": {
                        "target_tokens": TensorData(data=[1, 2, 3], dtype="float32"),
                        "weights": TensorData(data=[1.0, 1.0, 1.0], dtype="float32"),
                    },
                },
            ),
            "dtype",
        ),
        (
            "custom_forward_backward",
            cast(
                Any,
                {
                    "model_input": ModelInput(
                        chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))]
                    ),
                    "loss_fn_inputs": {},
                },
            ),
            "target_tokens",
        ),
    ],
)
def test_training_operations_reject_invalid_loss_inputs_before_submission(
    method: str,
    sample: Sample,
    message: str,
) -> None:
    client = FakeClient()
    session = _make_session(client)

    with pytest.raises(ValueError, match=message):
        if method == "forward_backward":
            session.trainer.forward_backward(samples=[sample], loss=LossConfig(type="LOSS_TYPE_PPO"))
        elif method == "forward":
            session.trainer.forward(samples=[sample], loss=_CROSS_ENTROPY)
        else:
            session.trainer.custom_forward_backward(
                samples=[sample],
                gradients=[Gradient(data=[0.1, 0.2, 0.3], dtype="D_TYPE_FLOAT32")],
            )

    assert client.beta.rl.operations.last_call is None
    assert client.captured_put_body is None
    session.stop()


def test_forward_warns_but_submits_undeclared_loss_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """An undeclared tensor key warns and still ships.

    ``loss_fn_inputs`` is an open map on the wire, so a key this SDK has not heard of may
    be a server input newer than the client. Reusing one batch across ``forward`` and
    ``forward_backward`` is the ordinary native idiom and must not raise.
    """
    patch_wait(monkeypatch, _scored_result([-1.0, -2.0, -3.0]))
    client = FakeClient()
    session = _make_session(client)

    sample = Sample(
        model_input=ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3]))]),
        loss_fn_inputs={
            "target_tokens": TensorData(data=[1, 2, 3], dtype="int64"),
            "weights": TensorData(data=[1.0, 1.0, 1.0], dtype="float32"),
            "logprobs": TensorData(data=[-0.1, -0.2, -0.3], dtype="float32"),
        },
    )
    with pytest.warns(UserWarning, match="logprobs"):
        session.trainer.forward(samples=[sample], loss=_CROSS_ENTROPY)

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["samples"] == [_sample_payload(sample)]
    session.stop()


async def test_forward_backward_uploads_large_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding the threshold are uploaded; inline samples have truncated sequences."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=2.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    client = FakeClient()
    trainer = _make_session(client)

    long_tokens = list(range(20))
    long_weights = [1.0] * 20
    sample = Sample(
        model_input=ModelInput(
            chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=long_tokens))],
        ),
        loss_fn_inputs={
            "target_tokens": TensorData(data=long_tokens, dtype="int64"),
            "weights": TensorData(
                data=long_weights,
                dtype="float32",
            ),
        },
    )

    result = await trainer.trainer.forward_backward_async(
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
    assert sent["loss_fn_inputs"]["weights"]["data"] == long_weights[:8]


def test_forward_backward_rejects_non_finite_tensor_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """JSON cannot carry -inf, so it must be caught before the payload is uploaded."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    client = FakeClient()
    trainer = _make_session(client)

    with pytest.raises(ValueError, match="NaN or infinite"):
        trainer.trainer.forward_backward(
            samples=[
                Sample(
                    model_input=ModelInput(
                        chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=list(range(20))))],
                    ),
                    loss_fn_inputs={
                        "target_tokens": TensorData(data=list(range(20)), dtype="int64"),
                        "weights": TensorData(data=[float("-inf")] + [1.0] * 19, dtype="float32"),
                    },
                )
            ],
            loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
        )

    assert client.captured_put_body is None
    trainer.stop()


def test_forward_backward_rejects_payload_above_max(monkeypatch: pytest.MonkeyPatch) -> None:
    """Payloads exceeding R2's single-PUT limit raise before any upload is attempted."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 10)
    monkeypatch.setattr(rl_payloads_module, "_MAX_PAYLOAD_SIZE", 20)
    client = FakeClient()
    trainer = _make_session(client)

    with pytest.raises(ValueError, match="exceeds"):
        trainer.trainer.forward_backward(
            samples=[
                Sample(
                    model_input=ModelInput(
                        chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=list(range(50))))],
                    ),
                    loss_fn_inputs={
                        "target_tokens": TensorData(data=list(range(50)), dtype="int64"),
                        "weights": TensorData(data=[1.0] * 50, dtype="float32"),
                    },
                )
            ],
            loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
        )

    assert client.captured_put_body is None
    trainer.stop()


@pytest.mark.parametrize("method", ["forward", "forward_backward", "custom_forward_backward"])
def test_weights_mask_conflict_before_upload(monkeypatch: pytest.MonkeyPatch, method: str) -> None:
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 1)
    client = FakeClient()
    session = _make_session(client)
    sample = _small_sample()
    sample["loss_fn_inputs"] = {**sample["loss_fn_inputs"], "mask": TensorData(data=[1, 1, 1], dtype="int64")}
    kwargs: dict[str, Any] = {"samples": [sample]}
    if method == "custom_forward_backward":
        kwargs["gradients"] = [Gradient(data=[0.1, 0.2, 0.3], dtype="D_TYPE_FLOAT32")]
    else:
        kwargs["loss"] = _CROSS_ENTROPY
    try:
        with pytest.raises(ValueError, match="cannot contain both weights and mask"):
            getattr(session.trainer, method)(**kwargs)
        assert client.beta.rl.operations.last_call is None
        assert client.captured_put_body is None
    finally:
        session.stop()


@pytest.mark.parametrize("method", ["forward", "forward_backward"])
@pytest.mark.parametrize("beta", [0.0, 0.1])
@pytest.mark.parametrize("reference", [False, True])
def test_grpo_reference_requirement(monkeypatch: pytest.MonkeyPatch, method: str, beta: float, reference: bool) -> None:
    monkeypatch.setattr(rl_payloads_module, "_LARGE_PAYLOAD_THRESHOLD", 1)
    patch_wait(monkeypatch, _scored_result([-1.0, -2.0, -3.0]))
    client = FakeClient()
    session = _make_session(client)
    sample = _policy_sample(reference_logprobs=reference)
    loss = LossConfig(type="LOSS_TYPE_GRPO", grpo_params={"beta": beta})
    try:
        if beta > 0 and not reference:
            with pytest.raises(ValueError, match="reference_logprobs"):
                getattr(session.trainer, method)(samples=[sample], loss=loss)
            assert client.beta.rl.operations.last_call is None
            assert client.captured_put_body is None
        else:
            getattr(session.trainer, method)(samples=[sample], loss=loss)
            assert client.beta.rl.operations.last_call is not None
            assert client.captured_put_body is not None
    finally:
        session.stop()
