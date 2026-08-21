from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.unit.rl_wait import patch_wait
from tests.unit._rl_fakes import FakeClient
from together.lib.beta.rl import (
    Sample,
    Logprob,
    Trainer,
    Weights,
    Gradient,
    Generator,
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
    trainer as trainer_module,
    generator as generator_module,
)
from together.types.beta.rl.sample_operation import SampleOperation


def _make_session(client: FakeClient | None = None) -> SessionClient:
    if client is None:
        client = FakeClient()
    return SessionClient("sess", _client=cast(Any, client))


def _sample_payload(sample: Sample) -> dict[str, Any]:
    return dict(sample)


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


def test_forward_passes_samples(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_wait(
        monkeypatch,
        ForwardResult(logprobs=[Logprob(data=[-1.0, -2.0, -3.0])]),
    )
    client = FakeClient()
    trainer = _make_session(client)

    samples = [_small_sample()]
    result = trainer.trainer.forward(samples=samples)

    assert result.logprobs[0].data == [-1.0, -2.0, -3.0]
    assert client.beta.rl.operations.last_call is not None
    method, args, kwargs = client.beta.rl.operations.last_call
    assert method == "forward"
    assert args == ("sess",)
    assert kwargs["samples"] == [_sample_payload(sample) for sample in samples]
    assert kwargs.get("extra_body") is None
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

    result = trainer.trainer.weights_sync(weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")

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


async def test_stop_async_closes_client() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value={"id": "stop-op"})
    client.close = AsyncMock()
    trainer = SessionClient("sess", _client=cast(Any, client))

    result = await trainer.stop_async()

    assert result == {"id": "stop-op"}
    assert trainer._loop.closed
    client.beta.rl.sessions.stop.assert_awaited_once_with("sess")
    client.close.assert_awaited_once()


def test_stop_marks_the_handle_closed() -> None:
    client = MagicMock()
    client.beta.rl.sessions.stop = AsyncMock(return_value={"id": "stop-op"})
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
        loss_inputs=LossInputs(
            target_tokens=LossTargetTokens(data=[1, 2, 3], dtype="D_TYPE_INT64"),
            weights=Weights(
                data=(value for value in (1.0, 0.0, 1.0)),
                dtype="D_TYPE_FLOAT32",
            ),
        ),
    )
    trainer.trainer.forward_backward(
        samples=[sample],
        loss=LossConfig(type="LOSS_TYPE_CROSS_ENTROPY"),
    )

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["samples"][0]["loss_inputs"]["weights"]["data"] == [1.0, 0.0, 1.0]
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

    assert trainer_module._resolve_loss_type(loss) == {"type": expected, "grpo_params": {"beta": 0.1}}
    assert loss["type"] == given, "input config must not be mutated"


def test_resolve_loss_type_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="Unknown loss type"):
        trainer_module._resolve_loss_type(cast(Any, {"type": "gspo"}))


def test_forward_backward_sends_proto_loss_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Short loss names reach the API in their proto spelling."""
    patch_wait(monkeypatch, ForwardBackwardResult(loss=0.5, metrics={}))
    client = FakeClient()
    trainer = _make_session(client)

    trainer.trainer.forward_backward(samples=[_small_sample()], loss=cast(Any, {"type": "ppo"}))

    assert client.beta.rl.operations.last_call is not None
    _, _, kwargs = client.beta.rl.operations.last_call
    assert kwargs["loss"] == {"type": "LOSS_TYPE_PPO"}
    trainer.stop()


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
        loss_inputs=LossInputs(
            target_tokens=LossTargetTokens(data=long_tokens, dtype="D_TYPE_INT64"),
            weights=Weights(
                data=long_weights,
                dtype="D_TYPE_FLOAT32",
            ),
        ),
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
    assert sent["loss_inputs"]["weights"]["data"] == long_weights[:8]


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
