from __future__ import annotations

import signal
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("tinker")

import numpy as np
from tinker import types
from tinker.types.image_chunk import ImageChunk

from together.lib.beta.rl import tinker as tinker_compat
from together.lib.beta.rl.tinker import _service, _sampling, _teardown, _training, _converters
from together.lib.beta.rl.clients.session import SessionClient
from together.types.beta.rl.sample_result import SampleResult
from together.types.beta.rl.sampled_sequence import SampledSequence
from together.types.beta.rl.prompt_top_logprobs import PromptTopLogprobs
from together.types.beta.rl.forward_backward_result import ForwardBackwardResult

_OPERATION = {"id": "op-1", "status": "TRAINING_OPERATION_STATUS_PENDING"}


def _noop() -> None:
    pass


def _ignore(_value: Any) -> None:
    pass


def _return_resources(resources: Any) -> Callable[..., Any]:
    def create(**_: Any) -> Any:
        return resources

    return create


def _session_with_operations(**operations: Any) -> SessionClient:
    client = SimpleNamespace(beta=SimpleNamespace(rl=SimpleNamespace(operations=SimpleNamespace(**operations))))
    return SessionClient("sess", _client=cast(Any, client))


def _close(session: SessionClient) -> None:
    if session._event_loop is not None:
        session._event_loop.close()


def _patch_submit_and_wait(monkeypatch: pytest.MonkeyPatch, result: Any = None) -> list[float | None]:
    """Stub out polling; returns the list of timeouts it was called with."""
    timeouts: list[float | None] = []

    async def fake(_self: Any, _operation: Any, *, timeout: float | None, interval: float) -> Any:  # noqa: ARG001
        timeouts.append(timeout)
        return result

    monkeypatch.setattr(SessionClient, "_submit_and_wait", fake)
    return timeouts


def _rl_loop_datum() -> types.Datum:
    """A Datum built exactly the way tinker's rl_loop.py builds one.

    Prompt [1, 2, 3, 4], sampled response [10, 11, 12]: model_input drops the final
    sampled token and the arrays are already shifted to align with next-token targets.
    Float values are exactly representable in float32 so equality stays exact.
    """
    prompt = types.ModelInput.from_ints([1, 2, 3, 4])
    sampled = [10, 11, 12]
    model_input = prompt.append(types.EncodedTextChunk(tokens=sampled[:-1]))
    ob_len = prompt.length - 1
    return types.Datum(
        model_input=model_input,
        loss_fn_inputs={
            "target_tokens": types.TensorData([0] * ob_len + sampled, dtype="int64"),
            "logprobs": types.TensorData([0.0] * ob_len + [-0.5, -0.25, -0.125], dtype="float32"),
            "advantages": types.TensorData([0.0] * ob_len + [0.5] * len(sampled), dtype="float32"),
        },
    )


def test_datum_arrays_pass_through_unshifted() -> None:
    """The arrays must NOT be shifted again: rl_loop pre-shifts them, and a second
    shift (e.g. apply_label_shift) would silently train against the wrong targets."""
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling_inputs")

    inputs = sample["loss_inputs"]
    assert "target_tokens" in inputs
    assert "importance_sampling_inputs" in inputs
    assert inputs["target_tokens"]["data"] == [0, 0, 0, 10, 11, 12]
    assert inputs["importance_sampling_inputs"]["logprobs"]["data"] == [0.0, 0.0, 0.0, -0.5, -0.25, -0.125]
    assert inputs["importance_sampling_inputs"]["advantages"]["data"] == [0.0, 0.0, 0.0, 0.5, 0.5, 0.5]


def test_datum_converts_field_for_field() -> None:
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling_inputs")

    chunks = sample["model_input"]["chunks"]
    assert isinstance(chunks, list)
    assert [chunk["encoded_text"]["tokens"] for chunk in chunks] == [[1, 2, 3, 4], [10, 11]]
    assert "policy_segments" not in sample
    # weights deliberately omitted: advantages mask the prompt positions already
    assert "weights" not in sample["loss_inputs"]
    # dtype is not optional — the server rejects a tensor whose element type it would
    # have to guess ("value must be in list [1]" on target_tokens.dtype).
    inputs = sample["loss_inputs"]
    target_tokens: dict[str, Any] = dict(inputs.get("target_tokens") or {})
    is_inputs: dict[str, Any] = dict(inputs.get("importance_sampling_inputs") or {})
    assert target_tokens.get("dtype") == "D_TYPE_INT64"
    assert is_inputs.get("logprobs", {}).get("dtype") == "D_TYPE_FLOAT32"
    assert is_inputs.get("advantages", {}).get("dtype") == "D_TYPE_FLOAT32"


def test_model_input_rejects_non_text_chunks() -> None:
    with pytest.raises(ValueError, match="encoded_text"):
        _converters._to_model_input(types.ModelInput(chunks=[ImageChunk(data=b"", format="png")]))


def test_loss_inputs_key_matches_wire_field() -> None:
    assert _converters._loss_inputs_key("LOSS_TYPE_IMPORTANCE_SAMPLING") == "importance_sampling_inputs"
    assert _converters._loss_inputs_key("ppo") == "ppo_inputs"


def test_loss_inputs_key_rejects_losses_the_conversion_does_not_fit() -> None:
    """cross_entropy Datums carry weights, not logprobs/advantages, and cispo Datums
    carry extra clip thresholds — converting them with the hardcoded pair would either
    crash confusingly or silently train a different loss. grpo is Together-only."""
    with pytest.raises(ValueError, match="cross_entropy"):
        _converters._loss_inputs_key("LOSS_TYPE_CROSS_ENTROPY")
    with pytest.raises(ValueError, match="cispo"):
        _converters._loss_inputs_key("LOSS_TYPE_CISPO")
    with pytest.raises(ValueError, match="grpo"):
        _converters._loss_inputs_key("LOSS_TYPE_GRPO")


def test_forward_backward_output_maps_loss_into_tinker_metrics() -> None:
    """Tutorials read metrics['loss:sum']; Together reports the total as `.loss` instead.
    Per-datum loss_fn_outputs stay empty rather than inventing logprobs."""
    output = _converters._to_forward_backward_output(
        ForwardBackwardResult(loss=1.25, metrics={"loss/clip/high_fraction": 0.1})
    )

    assert isinstance(output, types.ForwardBackwardOutput)
    assert output.metrics == {"loss/clip/high_fraction": 0.1, "loss:sum": 1.25}
    assert output.loss_fn_outputs == []
    assert output.loss_fn_output_type == ""


def test_forward_backward_output_does_not_overwrite_existing_loss_sum() -> None:
    output = _converters._to_forward_backward_output(ForwardBackwardResult(loss=1.25, metrics={"loss:sum": 9.0}))

    assert output.metrics["loss:sum"] == 9.0


def test_to_sample_rejects_missing_loss_inputs() -> None:
    """A cookbook Datum missing advantages must fail with ValueError, not a bare KeyError."""
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([1, 2], dtype="int64"),
            "logprobs": types.TensorData([0.0, -0.1], dtype="float32"),
        },
    )
    with pytest.raises(ValueError, match="missing \\['advantages'\\]"):
        _converters._to_sample(datum, "importance_sampling_inputs")


def test_loss_fn_config_routes_only_supported_keys() -> None:
    """A misspelled clipping threshold must fail instead of silently changing PPO's objective."""
    loss = _training._to_loss_config(
        "ppo",
        {"clip_low_threshold": 0.9, "clip_high_threshold": 1.1},
    )

    assert "ppo_params" in loss
    assert loss["ppo_params"] == {
        "clip_low_threshold": 0.9,
        "clip_high_threshold": 1.1,
    }
    with pytest.raises(ValueError, match="accepted keys.*clip_high_threshold"):
        _training._to_loss_config("ppo", {"clip_hgh_threshold": 1.1})


def test_sampling_params_inject_tinker_defaults() -> None:
    """Unset wire fields fall through to server defaults, so tinker's defaults must be sent."""
    converted = _converters._to_sampling_params(types.SamplingParams(max_tokens=16, stop="Human:"))

    assert converted == {
        "temperature": 1.0,
        "top_k": -1,
        "top_p": 1.0,
        "max_tokens": 16,
        "stop": ["Human:"],
    }


def test_sampling_params_drop_token_id_stops() -> None:
    """Dropping a renderer's non-EOS turn delimiter must warn that trajectories can differ."""
    with pytest.warns(UserWarning, match="trajectories can differ"):
        converted = _converters._to_sampling_params(types.SamplingParams(stop=[13]))

    assert "stop" not in converted


def test_adam_params_send_grad_clip_norm_off() -> None:
    """tinker's grad_clip_norm=0.0 default means no clipping; unset would inherit the
    session default of 1.0 and the two backends would train differently."""
    converted = _converters._to_adam_params(types.AdamParams(learning_rate=4e-5, beta1=0.9, beta2=0.95, eps=1e-8))

    assert converted == {
        "learning_rate": 4e-5,
        "beta1": 0.9,
        "beta2": 0.95,
        "eps": 1e-8,
        "weight_decay": 0.0,
        "grad_clip_norm": 0.0,
    }


def test_sample_response_normalizes_wire_shapes() -> None:
    result = SampleResult(
        policy_segments=[],
        sequences=[
            SampledSequence(
                prompt_cache_hit_tokens=0,
                stop_reason="STOP_REASON_STOP",
                tokens=["10", 11],  # int64 arrives as strings on the wire
                logprobs=[-0.5, -0.25],
            ),
            SampledSequence(
                prompt_cache_hit_tokens=0,
                stop_reason="STOP_REASON_LENGTH",
                tokens=[12],
                logprobs=None,
            ),
        ],
    )

    response = _converters._to_sample_response(result)

    first, second = response.sequences
    assert first.tokens_np is not None and first.tokens_np.dtype == np.int32
    assert first.tokens == [10, 11]
    assert first.logprobs == [-0.5, -0.25]
    assert first.stop_reason == "stop"
    assert second.tokens == [12]
    assert second.logprobs is None
    assert second.stop_reason == "length"


def test_sample_response_converts_prompt_logprobs_to_tinker_shapes() -> None:
    """Wire placeholders must become Tinker's NaN/sentinel rows without shifting prompt positions."""
    result = SampleResult(
        policy_segments=[],
        sequences=[
            SampledSequence(
                prompt_cache_hit_tokens=2,
                stop_reason="STOP_REASON_STOP",
                tokens=[1],
                logprobs=[-0.1],
            )
        ],
        prompt_logprobs=[0.0, -0.25],
        topk_prompt_logprobs=[
            PromptTopLogprobs(token_ids=[], logprobs=[]),
            PromptTopLogprobs(token_ids=[8, 9], logprobs=[-0.2, -0.3]),
        ],
    )

    response = _converters._to_sample_response(result, topk_prompt_logprobs=3)

    assert response.prompt_logprobs_np is not None
    assert np.isnan(response.prompt_logprobs_np[0])
    assert response.prompt_logprobs == [None, pytest.approx(-0.25)]
    assert response.topk_prompt_logprobs_np is not None
    assert response.topk_prompt_logprobs_np.token_ids.shape == (2, 3)
    assert response.topk_prompt_logprobs == [None, [(8, pytest.approx(-0.2)), (9, pytest.approx(-0.3))]]
    assert response.prompt_cache_hit_tokens == 2


def test_sample_forwards_prompt_logprob_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Distillation requests must reach both wire flags instead of returning empty compatibility fields."""
    submitted: list[dict[str, Any]] = []

    async def submit(_session: SessionClient, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    monkeypatch.setattr(_sampling, "_submit_sample_batch", submit)
    session = _session_with_operations()
    tinker_compat.SamplingClient(session).sample(
        types.ModelInput.from_ints([1]),
        1,
        types.SamplingParams(max_tokens=1),
        include_prompt_logprobs=True,
        topk_prompt_logprobs=7,
    )

    assert submitted[0]["prompt_logprobs"] is True
    assert submitted[0]["topk_prompt_logprobs"] == 7
    with pytest.raises(ValueError, match="between 0 and 20"):
        tinker_compat.SamplingClient(session).sample(
            types.ModelInput.from_ints([1]),
            1,
            types.SamplingParams(max_tokens=1),
            topk_prompt_logprobs=21,
        )
    _close(session)


def test_module_reexports_types_without_genuine_clients() -> None:
    """Types come from tinker.types; Together clients must not leak real tinker ones."""
    assert tinker_compat.types is types
    assert tinker_compat.Datum is types.Datum
    assert tinker_compat.ModelInput is types.ModelInput
    assert tinker_compat.APIFuture is not __import__("tinker").APIFuture
    assert not hasattr(tinker_compat, "RestClient")
    assert not hasattr(tinker_compat, "resources")
    with pytest.raises(AttributeError, match="RestClient"):
        _ = tinker_compat.RestClient


def test_create_lora_training_client_warns_on_reproducibility_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(**_: object) -> None:
        raise RuntimeError("no network in unit tests")

    monkeypatch.setattr(_service.ModelResourcesClient, "create", refuse)
    # keep the real process-wide SIGTERM handler out of the test suite
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.warns(UserWarning, match="train_mlp"), pytest.raises(RuntimeError):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", train_mlp=False)


def test_create_lora_training_client_forwards_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    resources = MagicMock()
    resources.model_resources_id = "mr-1"
    resources.create_session.side_effect = RuntimeError("stop")
    monkeypatch.setattr(_service.ModelResourcesClient, "create", _return_resources(resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(RuntimeError, match="stop"):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", rank=16, seed=7)

    resources.create_session.assert_called_once_with(lora_config={"rank": 16, "seed": 7})
    resources.stop.assert_called_once_with()


def test_create_lora_training_client_rejects_unknown_kwargs() -> None:
    """A misspelled rank must fail instead of silently provisioning rank 32."""
    with pytest.raises(TypeError, match="rnak"):
        tinker_compat.ServiceClient().create_lora_training_client("model", rnak=8)  # type: ignore[call-arg]


def test_service_client_accepts_known_ignored_kwargs() -> None:
    """Paste-friendly Tinker HTTP options must not break construction."""
    client = tinker_compat.ServiceClient(
        default_headers={"X-Foo": "bar"},
        timeout=30.0,
        max_retries=3,
    )
    assert client._model_resources_id is None


def test_service_client_rejects_unknown_kwargs() -> None:
    with pytest.raises(TypeError, match="not_a_real_kwarg"):
        tinker_compat.ServiceClient(not_a_real_kwarg=1)


def test_attached_resources_are_detached_but_not_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Closing a borrowed resource must stop our session without deallocating another owner's GPUs."""
    session = MagicMock()
    resources = MagicMock()
    resources.retrieve.return_value = SimpleNamespace(base_model="model", lora_enabled=True)
    resources.create_session.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "attach", _return_resources(resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    training = tinker_compat.ServiceClient(model_resources_id="mr-1").create_lora_training_client("model")
    training.close()
    training.close()

    session.stop.assert_called_once_with()
    resources.detach.assert_called_once_with()
    resources.stop.assert_not_called()


def test_created_resources_close_with_context_manager(monkeypatch: pytest.MonkeyPatch) -> None:
    """The additive context manager must promptly release sessions and resources in notebooks."""
    session = MagicMock()
    resources = MagicMock()
    resources.create_session.return_value = session
    monkeypatch.setattr(_service.ModelResourcesClient, "create", _return_resources(resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)
    monkeypatch.setattr(_service, "_stop_on_exit", _ignore)

    with tinker_compat.ServiceClient().create_lora_training_client("model") as training:
        assert isinstance(training, tinker_compat.TrainingClient)

    session.stop.assert_called_once_with()
    resources.stop.assert_called_once_with()
    resources.detach.assert_not_called()


def test_attach_rejects_wrong_base_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Attaching must not silently train a different base model than the caller requested."""
    resources = MagicMock()
    resources.retrieve.return_value = SimpleNamespace(base_model="other", lora_enabled=True)
    monkeypatch.setattr(_service.ModelResourcesClient, "attach", _return_resources(resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(ValueError, match="other"):
        tinker_compat.ServiceClient(model_resources_id="mr-1").create_lora_training_client("model")

    resources.detach.assert_called_once_with()
    resources.create_session.assert_not_called()


def test_attach_rejects_resources_without_lora(monkeypatch: pytest.MonkeyPatch) -> None:
    """A LoRA client must fail before session creation when borrowed resources are full-weight."""
    resources = MagicMock()
    resources.retrieve.return_value = SimpleNamespace(base_model="model", lora_enabled=False)
    monkeypatch.setattr(_service.ModelResourcesClient, "attach", _return_resources(resources))
    monkeypatch.setattr(_service, "_exit_on_sigterm", _noop)

    with pytest.raises(ValueError, match="do not support LoRA"):
        tinker_compat.ServiceClient(model_resources_id="mr-1").create_lora_training_client("model")

    resources.detach.assert_called_once_with()
    resources.create_session.assert_not_called()


def test_save_weights_publishes_synchronously(monkeypatch: pytest.MonkeyPatch) -> None:
    """SYNCHRONOUS so the returned SamplingClient sees the updated policy;
    BACKGROUND_PUBLISH would silently turn the loop off-policy."""
    timeouts = _patch_submit_and_wait(monkeypatch)
    weights_sync = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(weights_sync=weights_sync)

    sampling = tinker_compat.TrainingClient(session).save_weights_and_get_sampling_client()

    weights_sync.assert_awaited_once_with("sess", weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS")
    assert timeouts == [None]
    assert isinstance(sampling, tinker_compat.SamplingClient)
    _close(session)


def test_sampling_client_is_valid_until_the_next_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    """The normal publish/sample/train loop must work, then an old client must fail after republish."""
    _patch_submit_and_wait(monkeypatch)
    session = _session_with_operations(weights_sync=AsyncMock(return_value=_OPERATION))
    submitted: list[dict[str, Any]] = []

    async def submit(_session: SessionClient, **kwargs: Any) -> dict[str, Any]:
        submitted.append(kwargs)
        return _OPERATION

    monkeypatch.setattr(_sampling, "_submit_sample_batch", submit)
    training = tinker_compat.TrainingClient(session)
    first = training.save_weights_and_get_sampling_client()
    first.sample(
        types.ModelInput.from_ints([1]),
        1,
        types.SamplingParams(max_tokens=1),
    )
    training.save_weights_and_get_sampling_client()

    assert len(submitted) == 1
    with pytest.raises(RuntimeError, match="snapshot checkpoints are not supported"):
        first.sample(
            types.ModelInput.from_ints([1]),
            1,
            types.SamplingParams(max_tokens=1),
        )
    _close(session)


def test_pending_result_waits_without_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """tinker futures wait indefinitely, and a long rollout easily outlives the SDK's
    default 300 s operation deadline — normalizing to DEFAULT_OPERATION_TIMEOUT would
    kill hour-long steps mid-loop."""
    timeouts = _patch_submit_and_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))

    tinker_compat.TrainingClient(session).optim_step(types.AdamParams(learning_rate=1e-4)).result()

    assert timeouts == [None]
    _close(session)


def test_pending_result_forwards_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tinker's timeout argument must bound polling instead of raising TypeError."""
    timeouts = _patch_submit_and_wait(monkeypatch)
    session = _session_with_operations(optim_step=AsyncMock(return_value=_OPERATION))

    tinker_compat.TrainingClient(session).optim_step(types.AdamParams(learning_rate=1e-4)).result(timeout=2.5)

    assert timeouts == [2.5]
    _close(session)


def test_forward_backward_result_is_tinker_shaped(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolving forward_backward must yield ForwardBackwardOutput with loss:sum, not invent logprobs."""
    _patch_submit_and_wait(monkeypatch, {"loss": 0.5, "metrics": {"loss/kl_ref/mean": 0.01}})
    session = _session_with_operations(forward_backward=AsyncMock(return_value=_OPERATION))

    output = tinker_compat.TrainingClient(session).forward_backward([_rl_loop_datum()], "importance_sampling").result()

    assert isinstance(output, types.ForwardBackwardOutput)
    assert output.metrics["loss:sum"] == 0.5
    assert output.metrics["loss/kl_ref/mean"] == 0.01
    assert output.loss_fn_outputs == []
    _close(session)


def test_operations_post_eagerly_at_call_time() -> None:
    """grpo_gsm8k fires all sample POSTs before collecting any, and submits
    forward_backward + optim_step before resolving either; a lazy-submit refactor
    would serialize the whole loop with every other test still green."""
    submitted: list[str] = []

    def poster(name: str) -> Any:
        async def post(_session_id: str, **_kwargs: Any) -> dict[str, Any]:
            submitted.append(name)
            return _OPERATION

        return post

    session = _session_with_operations(
        forward_backward=poster("forward_backward"),
        optim_step=poster("optim_step"),
        sample=poster("sample"),
    )
    training = tinker_compat.TrainingClient(session)

    training.forward_backward([_rl_loop_datum()], "importance_sampling")
    training.optim_step(types.AdamParams(learning_rate=1e-4))
    assert submitted == ["forward_backward", "optim_step"]

    tinker_compat.SamplingClient(session).sample(
        types.ModelInput.from_ints([1, 2, 3]),
        num_samples=1,
        sampling_params=types.SamplingParams(max_tokens=4),
    )
    assert submitted == ["forward_backward", "optim_step", "sample"]
    _close(session)


def test_sample_result_resolves_payload_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """Large sample outputs arrive as payload_id stubs; dropping the
    resolve_result_payload hop looks redundant and passes every other test."""
    output = SimpleNamespace(payload_id="stub")
    _patch_submit_and_wait(monkeypatch, output)
    wire_result = SampleResult(
        policy_segments=[],
        sequences=[
            SampledSequence(
                prompt_cache_hit_tokens=0,
                stop_reason="STOP_REASON_STOP",
                tokens=["7", 8],
                logprobs=[-0.5, -0.25],
            )
        ],
    )
    resolved_with: list[Any] = []

    async def fake_resolve(_client: Any, *, session_id: str, result: Any) -> Any:  # noqa: ARG001
        resolved_with.append(result)
        return SimpleNamespace(results=[wire_result])

    monkeypatch.setattr(_sampling, "resolve_result_payload", fake_resolve)
    session = _session_with_operations(sample=AsyncMock(return_value=_OPERATION))

    response = (
        tinker_compat.SamplingClient(session)
        .sample(
            types.ModelInput.from_ints([1, 2, 3]),
            num_samples=1,
            sampling_params=types.SamplingParams(max_tokens=4),
        )
        .result()
    )

    assert resolved_with == [output]
    assert isinstance(response, types.SampleResponse)
    assert response.sequences[0].tokens == [7, 8]
    _close(session)


def test_stop_on_exit_and_sigterm_translation(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """The exit hook (threading._register_atexit, so it runs before concurrent.futures
    teardown) must release the GPUs even when session.stop fails, and must not raise:
    threading._shutdown runs callbacks in a plain loop, so an escaping exception aborts
    every teardown after it. SIGTERM's default disposition skips those hooks entirely,
    so it is translated into SystemExit — chaining any handler the host installed."""
    hooks: list[Any] = []
    monkeypatch.setattr(_teardown.threading, "_register_atexit", hooks.append)
    session = MagicMock()
    session.session_id = "sess"
    # KeyboardInterrupt: even a Ctrl-C during a hung session.stop() must not skip
    # the GPU teardown, so the hook has to catch BaseException, not just Exception.
    session.stop.side_effect = KeyboardInterrupt()
    model_resources = MagicMock()
    model_resources.model_resources_id = "mr-123"
    model_resources.stop.side_effect = RuntimeError("teardown failed")

    lifecycle = _teardown._Lifecycle(
        cast(Any, session),
        cast(Any, model_resources),
        owns_model_resources=True,
    )
    _teardown._stop_on_exit(lifecycle)

    (hook,) = hooks
    hook()
    model_resources.stop.assert_called_once_with()
    assert "mr-123" in caplog.text
    assert lifecycle.closed is False
    assert lifecycle.session is session
    assert lifecycle.model_resources is model_resources

    monkeypatch.setattr(_teardown, "_sigterm_translated", False)
    chained: list[int] = []

    def previous_handler(signum: int, _frame: Any) -> None:
        chained.append(signum)

    def get_signal(_sig: int) -> Callable[[int, Any], None]:
        return previous_handler

    monkeypatch.setattr(_teardown.signal, "getsignal", get_signal)
    installed: dict[int, Any] = {}

    def install_signal(sig: int, handler: Any) -> Any:
        return installed.setdefault(sig, handler)

    monkeypatch.setattr(_teardown.signal, "signal", install_signal)

    _teardown._exit_on_sigterm()

    handler = installed[signal.SIGTERM]
    with pytest.raises(SystemExit) as excinfo:
        handler(signal.SIGTERM, None)
    assert excinfo.value.code == 128 + signal.SIGTERM
    assert chained == [signal.SIGTERM]


def test_failed_explicit_close_can_be_retried() -> None:
    """A failed close() must not mark the lifecycle closed, or GPUs become unreachable."""
    session = MagicMock()
    session.session_id = "sess"
    session.stop.side_effect = RuntimeError("busy")
    model_resources = MagicMock()
    model_resources.model_resources_id = "mr-1"
    lifecycle = _teardown._Lifecycle(
        cast(Any, session),
        cast(Any, model_resources),
        owns_model_resources=True,
    )

    with pytest.raises(RuntimeError, match="busy"):
        lifecycle.close()

    assert lifecycle.closed is False
    assert lifecycle.session is session
    assert lifecycle.model_resources is None
    model_resources.stop.assert_called_once_with()

    session.stop.side_effect = None
    try:
        lifecycle.close()
    except Exception as exc:  # pragma: no cover
        raise AssertionError(f"retry close should succeed: {exc}") from exc
    assert lifecycle.closed is True
    assert lifecycle.session is None
