from __future__ import annotations

from typing import Any, cast, get_args

import pytest

pytest.importorskip("tinker")

import numpy as np
from tinker import types
from tinker.types.image_chunk import ImageChunk

from together.lib.beta.rl import _losses as rl_losses
from tests.unit._rl_tinker import _tensors, _rl_loop_datum, _advantage_datum
from together.lib.beta.rl.tinker import _losses, _converters
from together.types.beta.rl.tensor_data import TensorData as WireTensorData
from together.types.beta.rl.sample_result import SampleResult
from together.types.beta.rl.loss_fn_output import LossFnOutput
from together.types.beta.rl.sampled_sequence import SampledSequence
from together.types.beta.rl.prompt_top_logprobs import PromptTopLogprobs
from together.types.beta.rl.forward_backward_result import ForwardBackwardResult


def test_datum_arrays_pass_through_unshifted() -> None:
    """The arrays must NOT be shifted again: rl_loop pre-shifts them, and a second
    shift (e.g. apply_label_shift) would silently train against the wrong targets."""
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling")

    inputs = sample["loss_fn_inputs"]
    assert inputs["target_tokens"]["data"] == [0, 0, 0, 10, 11, 12]
    assert inputs["logprobs"]["data"] == [0.0, 0.0, 0.0, -0.5, -0.25, -0.125]
    assert inputs["advantages"]["data"] == [0.0, 0.0, 0.0, 0.5, 0.5, 0.5]


def test_datum_converts_field_for_field() -> None:
    sample = _converters._to_sample(_rl_loop_datum(), "importance_sampling")

    chunks = sample["model_input"]["chunks"]
    assert isinstance(chunks, list)
    assert [chunk["encoded_text"]["tokens"] for chunk in chunks] == [[1, 2, 3, 4], [10, 11]]
    assert "policy_segments" not in sample
    inputs = sample["loss_fn_inputs"]
    assert inputs["target_tokens"]["dtype"] == "int64"
    assert inputs["logprobs"]["dtype"] == "float32"
    assert inputs["advantages"]["dtype"] == "float32"


def test_model_input_rejects_non_text_chunks() -> None:
    with pytest.raises(ValueError, match="encoded_text"):
        _converters._to_model_input(types.ModelInput(chunks=[ImageChunk(data=b"", format="png")]))


def test_tensor_shape_is_not_sent() -> None:
    """`shape` is redundant for a 1-D tensor, so the converter never sends it; _payloads
    separately strips it from the truncated inline validation body."""
    tensor = types.TensorData([2.0, 3.0, 4.0], dtype="float32", shape=[3])

    converted = _converters._to_tensor("advantages", tensor)

    assert converted == {"data": [2.0, 3.0, 4.0], "dtype": "float32"}


@pytest.mark.parametrize(
    ("tensor", "message"),
    [
        # Tinker CSR-encodes a 2-D torch tensor when that saves space...
        (
            types.TensorData(
                [2.0, 3.0],
                dtype="float32",
                shape=[2, 3],
                sparse_crow_indices=[0, 1, 2],
                sparse_col_indices=[1, 2],
            ),
            "'weights'.*sparse CSR",
        ),
        # ...and leaves it dense otherwise, which the wire shape rejects just the same.
        (types.TensorData([1.0, 0.0, 1.0, 1.0], dtype="float32", shape=[2, 2]), "'weights'.*2-dimensional"),
        # Nested lists leave `shape` unset, so rank has to come from the array itself —
        # reading the optional field would let this through and silently flatten it.
        (types.TensorData([[1.0, 0.0], [1.0, 1.0]], dtype="float32"), "'weights'.*2-dimensional"),
    ],
)
def test_multi_dimensional_tensor_is_rejected(tensor: types.TensorData, message: str) -> None:
    """Training operations take 1-D dense tensors only, so the request must fail here,
    naming the offending key, instead of coming back as an opaque server error."""
    with pytest.raises(ValueError, match=message):
        _converters._to_tensor("weights", tensor)


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


@pytest.mark.parametrize(
    ("loss_fn", "loss_fn_inputs", "message"),
    [
        ("importance_sampling", _tensors("logprobs", "advantages"), "must include.*'target_tokens'"),
        ("importance_sampling", _tensors("target_tokens", "logprobs"), "must include.*'advantages'"),
        ("cross_entropy", _tensors("target_tokens"), "must include.*'weights'"),
    ],
)
def test_to_sample_rejects_missing_required_inputs(
    loss_fn: types.LossFnType, loss_fn_inputs: dict[str, Any], message: str
) -> None:
    """A key the loss requires and the caller omitted is always the caller's error."""
    datum = types.Datum(model_input=types.ModelInput.from_ints([1, 2]), loss_fn_inputs=loss_fn_inputs)

    with pytest.raises(ValueError, match=message):
        _converters._to_sample(datum, loss_fn)


@pytest.mark.parametrize(
    ("loss_fn", "loss_fn_inputs", "message"),
    [
        ("importance_sampling", _tensors("target_tokens", "logprobs", "advantages", "unknown"), "keys.*'unknown'"),
        # reference_logprobs belongs to grpo only, which the wrapper does not support.
        (
            "importance_sampling",
            _tensors("target_tokens", "logprobs", "advantages", "reference_logprobs"),
            "keys.*'reference_logprobs'",
        ),
        # cross_entropy has no advantages term.
        ("cross_entropy", _tensors("target_tokens", "weights", "advantages"), "keys.*'advantages'"),
    ],
)
def test_to_sample_warns_but_forwards_undeclared_inputs(
    loss_fn: types.LossFnType, loss_fn_inputs: dict[str, Any], message: str
) -> None:
    """An undeclared key warns and still ships.

    ``loss_fn_inputs`` is an open map on the wire and tinker itself does no per-loss key
    validation, so a key this table has not heard of may be a scratch key or a server
    input newer than the SDK. Warning keeps the typo signal without making the SDK a gate.
    """
    datum = types.Datum(model_input=types.ModelInput.from_ints([1, 2]), loss_fn_inputs=loss_fn_inputs)

    with pytest.warns(UserWarning, match=message):
        sample = _converters._to_sample(datum, loss_fn)

    assert set(sample["loss_fn_inputs"]) == set(loss_fn_inputs)


@pytest.mark.parametrize(
    ("loss_fn", "config", "expected_type", "expected_params"),
    [
        ("cross_entropy", None, "LOSS_TYPE_CROSS_ENTROPY", None),
        ("importance_sampling", None, "LOSS_TYPE_IMPORTANCE_SAMPLING", None),
        (
            "ppo",
            {"clip_low_threshold": 0.9, "clip_high_threshold": 1.1},
            "LOSS_TYPE_PPO",
            ("ppo_params", {"clip_low_threshold": 0.9, "clip_high_threshold": 1.1}),
        ),
        (
            "cispo",
            {"clip_low_threshold": 0.1, "clip_high_threshold": 3.0},
            "LOSS_TYPE_CISPO",
            ("cispo_params", {"clip_low_threshold": 0.1, "clip_high_threshold": 3.0}),
        ),
        ("dro", {"beta": 0.01}, "LOSS_TYPE_DRO", ("dro_params", {"beta": 0.01})),
    ],
)
def test_loss_fn_config_routes_to_matching_params(
    loss_fn: types.LossFnType,
    config: dict[str, float] | None,
    expected_type: str,
    expected_params: tuple[str, Any] | None,
) -> None:
    loss = _converters._to_loss_config(loss_fn, config)

    assert loss["type"] == expected_type
    if expected_params is None:
        assert set(loss) == {"type"}
    else:
        key, value = expected_params
        assert loss[key] == value  # type: ignore[literal-required]


def test_unsupported_loss_fn_is_rejected() -> None:
    """grpo is a real Together loss the wrapper deliberately does not map, so a tinker
    script can reach both paths with it — each must say so rather than fail server-side."""
    loss_fn = "grpo"
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs=_tensors("target_tokens", "logprobs", "advantages"),
    )

    with pytest.raises(ValueError, match="Unknown loss_fn"):
        _converters._to_sample(datum, cast(Any, loss_fn))
    with pytest.raises(ValueError, match="Unknown loss_fn"):
        _converters._to_loss_config(cast(Any, loss_fn), None)


@pytest.mark.parametrize(
    ("loss_fn", "config", "message"),
    [
        # A misspelled threshold must fail instead of silently changing PPO's objective.
        ("ppo", {"clip_hgh_threshold": 1.1}, "accepted keys.*clip_high_threshold"),
        ("cross_entropy", {"beta": 0.1}, "Unsupported keys in loss_fn_config"),
        ("dro", None, "must include.*'beta'"),
        ("dro", {}, "must include.*'beta'"),
    ],
)
def test_loss_fn_config_key_validation(
    loss_fn: types.LossFnType, config: dict[str, float] | None, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _converters._to_loss_config(loss_fn, config)


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
    assert response.prompt_cache_hit_tokens == 0
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
    assert response.prompt_cache_hit_tokens == 2
    assert response.topk_prompt_logprobs_np is not None
    assert response.topk_prompt_logprobs_np.token_ids.shape == (2, 3)
    assert response.topk_prompt_logprobs == [None, [(8, pytest.approx(-0.2)), (9, pytest.approx(-0.3))]]


def test_tinker_loss_specs_share_native_contracts() -> None:
    for loss_fn, spec in _losses.LOSS_SPECS.items():
        assert spec is rl_losses.LOSS_SPECS[spec.wire_type], loss_fn


def test_loss_specs_cover_every_mappable_loss() -> None:
    assert set(_losses.LOSS_SPECS) == set(get_args(types.LossFnType))
    mapped = {spec.wire_type for spec in _losses.LOSS_SPECS.values()}
    assert set(rl_losses.LOSS_SPECS) - mapped == {"LOSS_TYPE_GRPO", "LOSS_TYPE_DPPO"}


@pytest.mark.parametrize(
    ("key", "dtype"),
    [("target_tokens", "float32"), ("advantages", "int64"), ("logprobs", "int64")],
)
def test_tensor_dtype_must_match_request_shape(key: str, dtype: types.TensorDtype) -> None:
    """Tinker coerces plain lists by key name, but a numpy/torch array keeps its own
    dtype — so `np.array([1, 0])` advantages would reach the server as an int64 tensor
    where the shape pins float32. That must fail here, naming the key."""
    with pytest.raises(ValueError, match=f"{key}.*has dtype"):
        _converters._to_tensor(key, types.TensorData([1, 0], dtype=dtype))


@pytest.mark.parametrize("key", ["weights", "mask"])
@pytest.mark.parametrize("dtype", ["int64", "float32"])
def test_union_typed_tensors_accept_either_dtype(key: str, dtype: types.TensorDtype) -> None:
    """weights/mask are the TensorData union, so neither dtype may be rejected."""
    assert _converters._to_tensor(key, types.TensorData([1, 0], dtype=dtype))["dtype"] == dtype


def test_ppo_datum_uses_flat_loss_fn_inputs() -> None:
    inputs = _converters._to_sample(_advantage_datum(), "ppo")["loss_fn_inputs"]

    assert inputs["logprobs"]["data"] == [0.0, -0.5, -0.25]
    assert inputs["advantages"]["data"] == [0.0, 0.5, 0.5]


def test_with_zero_weights_if_missing_synthesizes_zero_weights() -> None:
    """Tinker's custom-loss prep accepts a targets-only Datum; the CE wire shape requires weights."""
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={"target_tokens": types.TensorData([1, 2], dtype="int64")},
    )

    filled = _converters._with_zero_weights_if_missing(datum)

    assert filled.loss_fn_inputs["weights"].data == [0.0, 0.0]


def test_with_zero_weights_rejects_unexpected_keys() -> None:
    datum = types.Datum(
        model_input=types.ModelInput.from_ints([1, 2]),
        loss_fn_inputs={
            "target_tokens": types.TensorData([1, 2], dtype="int64"),
            "logprobs": types.TensorData([0.0, -0.1], dtype="float32"),
        },
    )

    with pytest.raises(ValueError, match="unexpected keys.*logprobs"):
        _converters._with_zero_weights_if_missing(datum)


def test_forward_output_fills_loss_fn_outputs_from_real_logprobs() -> None:
    output = _converters._to_forward_backward_output(
        ForwardBackwardResult(
            loss=0.5,
            loss_fn_outputs=[
                LossFnOutput(tensors={"logprobs": WireTensorData(data=values, dtype="float32")})
                for values in ([-0.1, -0.2], [-0.3])
            ],
        )
    )

    assert len(output.loss_fn_outputs) == 2
    assert output.loss_fn_outputs[0]["logprobs"].data == pytest.approx([-0.1, -0.2])
    assert output.loss_fn_outputs[1]["logprobs"].data == pytest.approx([-0.3])
    assert output.metrics == {"loss:sum": 0.5}


def test_unit_weights_replace_the_zero_weights_that_would_mask_logprobs() -> None:
    sample = _converters._to_sample(
        types.Datum(
            model_input=types.ModelInput.from_ints([1, 2]),
            loss_fn_inputs={
                "target_tokens": types.TensorData([1, 2], dtype="int64"),
                "weights": types.TensorData([0.0, 0.0], dtype="float32"),
            },
        ),
        "cross_entropy",
    )

    scored = _converters._with_unit_weights(sample)

    assert scored["loss_fn_inputs"]["weights"]["data"] == [1.0, 1.0]
    assert scored["loss_fn_inputs"]["target_tokens"]["data"] == [1, 2]


def test_compute_logprobs_shapes_first_token_to_none() -> None:
    """Tinker's first prompt logprob is undefined; callers expect ``None`` at index 0."""
    assert _converters._to_compute_logprobs([0.1, -0.2, -0.3]) == [None, -0.2, -0.3]
    assert _converters._to_compute_logprobs([]) == []
    assert _converters._to_compute_logprobs([0.5]) == [None]
