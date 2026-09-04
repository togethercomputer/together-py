"""Pure conversions between tinker types and Together's RL wire types."""

from __future__ import annotations

import warnings
from typing import Any, Literal, cast
from collections.abc import Mapping, Sequence

import numpy as np
from tinker.types.topk_prompt_logprobs import TopkPromptLogprobs

from .. import (
    Sample as WireSample,
    AdamParams as WireAdamParams,
    LossConfig as WireLossConfig,
    SampleResult,
    SamplingParams as WireSamplingParams,
    ForwardBackwardResult,
)
from ._compat import types
from ._losses import loss_spec
from .._losses import INPUT_DTYPES, validate_keys, validate_input_keys
from .....types.beta.rl.model_input_param import ModelInput as WireModelInput
from .....types.beta.rl.tensor_data_param import TensorDataParam as WireTensorData
from .....types.beta.rl.model_input_chunk_param import ModelInputChunk as WireModelInputChunk

_TOPK_MASK_LOGPROB = -99999.0


def _to_model_input(model_input: types.ModelInput) -> WireModelInput:
    chunks: list[WireModelInputChunk] = []
    for chunk in model_input.chunks:
        if not isinstance(chunk, types.EncodedTextChunk):
            msg = f"Together supports encoded_text chunks only, got {getattr(chunk, 'type', chunk)!r}"
            raise ValueError(msg)
        chunks.append({"encoded_text": {"tokens": list(chunk.tokens)}})
    return {"chunks": chunks}


def _to_tensor(key: str, tensor: types.TensorData) -> WireTensorData:
    """Serialize one tinker ``TensorData`` into its wire shape.

    Emits the flattened ``data`` and its ``dtype``. ``shape`` is deliberately omitted:
    only one-dimensional tensors get this far, so it is always ``[len(data)]`` and the
    server infers it.

    Args:
        key: The ``loss_fn_inputs`` entry being serialized, used to make errors actionable.
        tensor: The tinker tensor to serialize.

    Returns:
        The wire tensor with its ``data`` and ``dtype``.

    Raises:
        ValueError: If the tensor is multi-dimensional, which training operations
            reject (Tinker produces such tensors from 2-D torch ``target_tokens``/
            ``weights``, either dense or CSR-encoded), or if its dtype is not the one
            the request shape pins for ``key``.
    """
    # Checked before to_numpy(), which reconstructs a sparse tensor through torch. A
    # sparse tensor's `data` holds only the non-zero values, so it is unusable without
    # the CSR indices the wire shape cannot carry.
    if tensor.sparse_crow_indices is not None or tensor.sparse_col_indices is not None:
        raise ValueError(
            f"Datum.loss_fn_inputs[{key!r}] is a sparse CSR tensor (shape {tensor.shape}), but training"
            " operations accept one-dimensional dense tensors only; flatten it before building the Datum."
        )
    # Rank comes from the array, not the optional `shape` field: a TensorData built
    # straight from nested lists holds a 2-D array and leaves `shape` unset, and its
    # `data` property would silently flatten it.
    array = tensor.to_numpy()
    if array.ndim != 1:
        raise ValueError(
            f"Datum.loss_fn_inputs[{key!r}] is {array.ndim}-dimensional, but training operations accept"
            " one-dimensional dense tensors only; flatten it before building the Datum."
        )
    # Tinker coerces plain lists by key name, but a numpy/torch array keeps its own
    # dtype, so this catches e.g. an integer `advantages` array before the server does.
    allowed = INPUT_DTYPES.get(key)
    if allowed is not None and tensor.dtype not in allowed:
        raise ValueError(
            f"Datum.loss_fn_inputs[{key!r}] has dtype {tensor.dtype!r}, but the request shape accepts"
            f" {sorted(allowed)}; use a {sorted(allowed)[0]} array instead."
        )
    # The cast narrows `tensor.dtype` (a plain str) onto the wire literal the dtype
    # check above already enforced. `array` is already 1-D, so tolist() skips the
    # extra copy `tensor.data` would flatten into.
    return cast("WireTensorData", {"data": array.tolist(), "dtype": tensor.dtype})


def _to_sample(datum: types.Datum, loss_fn: types.LossFnType) -> WireSample:
    """Serialize a tinker ``Datum`` into the wire sample shape ``loss_fn`` accepts.

    Each loss declares its own ``loss_fn_inputs`` shape, so the datum is validated
    against that loss rather than against the union of every loss's keys — otherwise
    a mismatch only surfaces as an opaque server rejection.

    Args:
        datum: The tinker datum to serialize.
        loss_fn: The loss the request will carry, which selects the accepted keys.

    Returns:
        The wire sample, with its tensors under ``loss_fn_inputs``.

    Raises:
        ValueError: If ``loss_fn`` is unsupported or a key the loss requires is missing.
            A key the loss does not declare warns and is forwarded.
    """
    spec = loss_spec(loss_fn)
    inputs = datum.loss_fn_inputs
    validate_input_keys(f"Datum.loss_fn_inputs for {loss_fn!r}", inputs.keys(), spec)
    return WireSample(
        model_input=_to_model_input(datum.model_input),
        loss_fn_inputs={key: _to_tensor(key, tensor) for key, tensor in inputs.items()},
    )


def _to_loss_config(loss_fn: types.LossFnType, config: Mapping[str, float] | None) -> WireLossConfig:
    """Map a tinker loss and its config onto Together's wire selector."""
    spec = loss_spec(loss_fn)
    values = config or {}
    validate_keys(
        f"loss_fn_config for {loss_fn!r}",
        values.keys(),
        required=spec.required_params,
        optional=spec.optional_params,
    )

    loss: dict[str, Any] = {"type": spec.wire_type}
    if values and spec.params_key is not None:
        loss[spec.params_key] = dict(values)
    return cast("WireLossConfig", loss)


def _with_unit_weights(sample: WireSample) -> WireSample:
    """Weight every position, so a scoring pass over the sample reads back true logprobs.

    A position its loss excludes comes back masked to zero. Without this, the zero weights
    the custom path prepares for the gradient operation would hide the very logprobs its
    client loss runs on.
    """
    target_tokens = sample["loss_fn_inputs"]["target_tokens"]
    weights = cast("WireTensorData", {"data": [1.0] * len(target_tokens["data"]), "dtype": "float32"})
    return WireSample(
        model_input=sample["model_input"],
        loss_fn_inputs={**sample["loss_fn_inputs"], "weights": weights},
    )


def _has_fractional_weights(sample: WireSample) -> bool:
    """Whether a converted sample's weights carry a value other than 0 or 1."""
    weights = sample["loss_fn_inputs"].get("weights")
    if weights is None:
        return False
    return not np.isin(weights["data"], (0, 1)).all()


def _warn_on_binarized_weights(samples: Sequence[WireSample], loss_fn: types.LossFnType) -> None:
    """Warn when a policy loss carries weights Together will read as a 0/1 mask.

    Tinker multiplies ``weights`` into the per-token loss for every loss; Together honors
    fractional values for ``cross_entropy`` only. Silently training a different objective
    is the failure this warns about, mirroring ``_stop_strings``.

    Args:
        samples: Converted samples about to be submitted.
        loss_fn: The loss they will be submitted under.
    """
    if loss_fn == "cross_entropy":
        return
    if any(_has_fractional_weights(sample) for sample in samples):
        warnings.warn(
            f"Together honors fractional loss_fn_inputs['weights'] for cross_entropy only; {loss_fn!r}"
            " treats every non-zero weight as 1, so gradients differ from Tinker's."
            " Use 'mask' when the intent is including or excluding tokens.",
            stacklevel=3,  # _warn_on_binarized_weights -> forward_backward -> caller
        )


def _with_zero_weights_if_missing(datum: types.Datum) -> types.Datum:
    """Match tinker's custom-loss prep: synthesize zero weights when only targets are present."""
    unexpected = sorted(set(datum.loss_fn_inputs) - {"target_tokens", "weights"})
    if unexpected:
        raise ValueError(
            "forward_backward_custom only supports loss_fn_inputs keys "
            f"{{'target_tokens', 'weights'}}; found unexpected keys: {unexpected}"
        )
    if "weights" in datum.loss_fn_inputs:
        return datum
    if "target_tokens" not in datum.loss_fn_inputs:
        raise ValueError("target_tokens must be provided when using cross_entropy")
    target_tokens = datum.loss_fn_inputs["target_tokens"]
    inputs = dict(datum.loss_fn_inputs)
    inputs["weights"] = types.TensorData([0.0] * len(target_tokens.data), dtype="float32")
    return types.Datum(model_input=datum.model_input, loss_fn_inputs=inputs)


def _to_forward_backward_output(result: ForwardBackwardResult) -> types.ForwardBackwardOutput:
    """Map Together's loss, metrics and per-sample outputs onto tinker's ForwardBackwardOutput.

    Together's total ``loss`` is published under ``metrics["loss:sum"]``, so scripts that
    only read ``.metrics`` keep working. Per-datum ``loss_fn_outputs`` carry real logprobs
    only when the operation was asked for them, which ``forward`` does and
    ``forward_backward`` does not; they stay empty otherwise, since inventing them would
    silently corrupt scripts that read them.
    """
    metrics = dict(result.metrics or {})
    metrics.setdefault("loss:sum", result.loss)
    return types.ForwardBackwardOutput(
        loss_fn_output_type="",
        loss_fn_outputs=[
            {"logprobs": types.TensorData(list(output.tensors["logprobs"].data), dtype="float32")}
            for output in result.loss_fn_outputs or []
        ],
        metrics=metrics,
    )


def _to_compute_logprobs(values: Sequence[float]) -> list[float | None]:
    """Tinker's first prompt logprob is undefined; callers expect ``None`` at index 0."""
    if not values:
        return []
    return [None, *[float(v) for v in values[1:]]]


def _stop_strings(stop: str | Sequence[str] | Sequence[int]) -> list[str]:
    """Keep string stops and warn when dropping token IDs the wire cannot carry."""
    if isinstance(stop, str):
        return [stop]
    strings = [item for item in stop if isinstance(item, str)]
    token_ids = [item for item in stop if not isinstance(item, str)]
    if token_ids:
        warnings.warn(
            f"Together's sampling stop takes strings only; ignoring token-id stops {token_ids}."
            " Generation will rely on the model's own end token, so trajectories can"
            " differ from Tinker when a dropped token is not that end token.",
            # Points at the conversion rather than counting frames up to the caller: the
            # depth differs per entry point, and the message names the offending stops.
            stacklevel=2,
        )
    return strings


def _to_sampling_params(params: types.SamplingParams) -> WireSamplingParams:
    # temperature/top_k/top_p are always sent: tinker's defaults live on the object,
    # while an unset field on our wire type would fall through to *server* defaults
    # and the two backends would quietly sample differently.
    converted = WireSamplingParams(temperature=params.temperature, top_k=params.top_k, top_p=params.top_p)
    if params.max_tokens is not None:
        converted["max_tokens"] = params.max_tokens
    if params.seed is not None:
        converted["seed"] = params.seed
    if params.stop is not None and (stop := _stop_strings(params.stop)):
        converted["stop"] = stop
    return converted


def _to_adam_params(params: types.AdamParams) -> WireAdamParams:
    # grad_clip_norm included: tinker's default 0.0 means "no clipping", while leaving
    # it unset here would inherit the session default of 1.0.
    return WireAdamParams(
        learning_rate=params.learning_rate,
        beta1=params.beta1,
        beta2=params.beta2,
        eps=params.eps,
        weight_decay=params.weight_decay,
        grad_clip_norm=params.grad_clip_norm,
    )


def _stop_reason(value: str) -> Literal["length", "stop"]:
    if value == "STOP_REASON_LENGTH":
        return "length"
    if value == "STOP_REASON_STOP":
        return "stop"
    raise ValueError(f"Unknown stop reason {value!r}")


def _prompt_logprobs(result: SampleResult) -> np.ndarray | None:
    if result.prompt_logprobs is None:
        return None
    values = np.asarray(result.prompt_logprobs, dtype=np.float32)
    if len(values):
        values[0] = np.nan
    return values


def _topk_prompt_logprobs(result: SampleResult, width: int) -> TopkPromptLogprobs | None:
    if result.topk_prompt_logprobs is None:
        return None
    token_ids = np.zeros((len(result.topk_prompt_logprobs), width), dtype=np.int32)
    logprobs = np.full((len(result.topk_prompt_logprobs), width), _TOPK_MASK_LOGPROB, dtype=np.float32)
    for row, alternatives in enumerate(result.topk_prompt_logprobs):
        row_token_ids = alternatives.token_ids or []
        row_logprobs = alternatives.logprobs or []
        if len(row_token_ids) != len(row_logprobs):
            raise ValueError(f"Prompt top-k token IDs and logprobs differ in length at position {row}")
        count = min(width, len(row_token_ids))
        token_ids[row, :count] = row_token_ids[:count]
        logprobs[row, :count] = row_logprobs[:count]
    return TopkPromptLogprobs(token_ids=token_ids, logprobs=logprobs)


def _to_sample_response(result: SampleResult, topk_prompt_logprobs: int = 0) -> types.SampleResponse:
    return types.SampleResponse(
        sequences=[
            types.SampledSequence(
                stop_reason=_stop_reason(sequence.stop_reason),
                # int64 tokens arrive as strings on the wire
                tokens_np=np.asarray([int(token) for token in sequence.tokens], dtype=np.int32),
                logprobs_np=None if sequence.logprobs is None else np.asarray(sequence.logprobs, dtype=np.float32),
            )
            for sequence in result.sequences
        ],
        prompt_logprobs_np=_prompt_logprobs(result),
        topk_prompt_logprobs_np=_topk_prompt_logprobs(result, topk_prompt_logprobs),
        prompt_cache_hit_tokens=result.sequences[0].prompt_cache_hit_tokens if result.sequences else 0,
    )
