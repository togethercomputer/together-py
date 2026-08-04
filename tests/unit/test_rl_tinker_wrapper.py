from __future__ import annotations

import signal
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("tinker")

from tinker import types

from together.lib.beta.rl import tinker as tinker_compat
from together.lib.beta.rl.tinker import _clients, _converters
from together.lib.beta.rl.clients.session import SessionClient
from together.types.beta.rl.sample_result import SampleResult
from together.types.beta.rl.sampled_sequence import SampledSequence

_OPERATION = {"id": "op-1", "status": "TRAINING_OPERATION_STATUS_PENDING"}


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
            "target_tokens": [0] * ob_len + sampled,
            "logprobs": [0.0] * ob_len + [-0.5, -0.25, -0.125],
            "advantages": [0.0] * ob_len + [0.5] * len(sampled),
        },
    )


def test_datum_arrays_pass_through_unshifted() -> None:
    """The arrays must NOT be shifted again: rl_loop pre-shifts them, and a second
    shift (e.g. apply_label_shift) would silently train against the wrong targets."""
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling_inputs")

    inputs = sample["loss_inputs"]
    assert inputs["target_tokens"]["data"] == [0, 0, 0, 10, 11, 12]
    assert inputs["importance_sampling_inputs"]["logprobs"]["data"] == [0.0, 0.0, 0.0, -0.5, -0.25, -0.125]
    assert inputs["importance_sampling_inputs"]["advantages"]["data"] == [0.0, 0.0, 0.0, 0.5, 0.5, 0.5]


def test_datum_converts_field_for_field() -> None:
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling_inputs")

    chunks = sample["model_input"]["chunks"]
    assert [chunk["encoded_text"]["tokens"] for chunk in chunks] == [[1, 2, 3, 4], [10, 11]]
    assert sample["policy_segments"] == []
    # weights deliberately omitted: advantages mask the prompt positions already
    assert "weights" not in sample["loss_inputs"]
    # dtype is not optional — the server rejects a tensor whose element type it would
    # have to guess ("value must be in list [1]" on target_tokens.dtype).
    inputs = sample["loss_inputs"]
    assert inputs["target_tokens"]["dtype"] == "D_TYPE_INT64"
    assert inputs["importance_sampling_inputs"]["logprobs"]["dtype"] == "D_TYPE_FLOAT32"
    assert inputs["importance_sampling_inputs"]["advantages"]["dtype"] == "D_TYPE_FLOAT32"


def test_model_input_rejects_non_text_chunks() -> None:
    fake = SimpleNamespace(chunks=[SimpleNamespace(type="image")])
    with pytest.raises(ValueError, match="encoded_text"):
        _converters._to_model_input(fake)


def test_loss_inputs_key_matches_wire_field() -> None:
    assert _converters._loss_inputs_key("LOSS_TYPE_IMPORTANCE_SAMPLING") == "importance_sampling_inputs"
    assert _converters._loss_inputs_key("LOSS_TYPE_GRPO") == "grpo_inputs"


def test_loss_inputs_key_rejects_losses_the_conversion_does_not_fit() -> None:
    """cross_entropy Datums carry weights, not logprobs/advantages, and cispo Datums
    carry extra clip thresholds — converting them with the hardcoded pair would either
    crash confusingly or silently train a different loss."""
    with pytest.raises(ValueError, match="cross_entropy"):
        _converters._loss_inputs_key("LOSS_TYPE_CROSS_ENTROPY")
    with pytest.raises(ValueError, match="cispo"):
        _converters._loss_inputs_key("LOSS_TYPE_CISPO")


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
    """Renderers report their stops as token ids (Qwen3.5: <|im_end|>, the EOS the
    generator already stops on), so they are warned about, not fatal."""
    with pytest.warns(UserWarning, match="token-id"):
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
    assert first.tokens == [10, 11]
    assert first.logprobs == [-0.5, -0.25]
    assert first.stop_reason == "stop"
    assert second.tokens == [12]
    assert second.logprobs is None
    assert second.stop_reason == "length"


def test_module_delegates_unknown_names_to_tinker() -> None:
    assert tinker_compat.types is types
    assert tinker_compat.Datum is types.Datum
    assert tinker_compat.ModelInput is types.ModelInput


def test_create_lora_training_client_warns_on_reproducibility_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(**_: object) -> None:
        raise RuntimeError("no network in unit tests")

    monkeypatch.setattr(_clients.ModelResourcesClient, "create", refuse)
    # keep the real process-wide SIGTERM handler out of the test suite
    monkeypatch.setattr(_clients, "_exit_on_sigterm", lambda: None)

    with pytest.warns(UserWarning, match="seed"), pytest.raises(RuntimeError):
        tinker_compat.ServiceClient().create_lora_training_client("Qwen/Qwen3.5-4B", seed=7)


def test_optim_step_pins_synchronous_weight_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    """SYNCHRONOUS publishes weights before the operation completes, which is what makes
    save_weights_and_get_sampling_client a pure handle; BACKGROUND_PUBLISH would silently
    turn the loop off-policy."""
    _patch_submit_and_wait(monkeypatch)
    optim_step = AsyncMock(return_value=_OPERATION)
    session = _session_with_operations(optim_step=optim_step)

    result = tinker_compat.TrainingClient(session).optim_step(types.AdamParams(learning_rate=1e-4)).result()

    optim_step.assert_awaited_once_with(
        "sess",
        weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
        adam_params=_converters._to_adam_params(types.AdamParams(learning_rate=1e-4)),
    )
    assert isinstance(result, types.OptimStepResponse)
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

    monkeypatch.setattr(_clients, "resolve_result_payload", fake_resolve)
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
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The exit hook (threading._register_atexit, so it runs before concurrent.futures
    teardown) must release the GPUs even when session.stop fails, and must not raise:
    threading._shutdown runs callbacks in a plain loop, so an escaping exception aborts
    every teardown after it. SIGTERM's default disposition skips those hooks entirely,
    so it is translated into SystemExit — chaining any handler the host installed."""
    hooks: list[Any] = []
    monkeypatch.setattr(_clients.threading, "_register_atexit", hooks.append)
    session = MagicMock()
    # KeyboardInterrupt: even a Ctrl-C during a hung session.stop() must not skip
    # the GPU teardown, so the hook has to catch BaseException, not just Exception.
    session.stop.side_effect = KeyboardInterrupt()
    model_resources = MagicMock()
    model_resources.model_resources_id = "mr-123"
    model_resources.stop.side_effect = RuntimeError("teardown failed")

    _clients._stop_on_exit(cast(Any, session), cast(Any, model_resources))

    (hook,) = hooks
    hook()
    model_resources.stop.assert_called_once_with()
    assert "mr-123" in capsys.readouterr().out

    monkeypatch.setattr(_clients, "_sigterm_translated", False)
    chained: list[int] = []
    monkeypatch.setattr(_clients.signal, "getsignal", lambda _sig: lambda signum, _frame: chained.append(signum))
    installed: dict[int, Any] = {}
    monkeypatch.setattr(_clients.signal, "signal", lambda sig, handler: installed.setdefault(sig, handler))

    _clients._exit_on_sigterm()

    handler = installed[signal.SIGTERM]
    with pytest.raises(SystemExit) as excinfo:
        handler(signal.SIGTERM, None)
    assert excinfo.value.code == 128 + signal.SIGTERM
    assert chained == [signal.SIGTERM]
