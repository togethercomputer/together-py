"""Pure conversions between tinker types and Together's RL wire types."""

from __future__ import annotations

import warnings
from typing import Any, Sequence, cast

import numpy as np

from .. import (
    Sample as WireSample,
    AdamParams as WireAdamParams,
    LossInputs,
    SampleResult,
    SamplingParams as WireSamplingParams,
)
from ._compat import types
from .....types.beta.rl.model_input_param import ModelInput as WireModelInput

_STOP_REASON = {"STOP_REASON_LENGTH": "length", "STOP_REASON_STOP": "stop"}


def _to_model_input(model_input: types.ModelInput) -> WireModelInput:
    chunks = []
    for chunk in model_input.chunks:
        if getattr(chunk, "type", None) != "encoded_text":
            msg = f"Together supports encoded_text chunks only, got {getattr(chunk, 'type', chunk)!r}"
            raise ValueError(msg)
        chunks.append({"encoded_text": {"tokens": list(chunk.tokens)}})
    return {"chunks": chunks}


_WIRE_DTYPE = {"int64": "D_TYPE_INT64", "float32": "D_TYPE_FLOAT32"}


def _to_tensor(tensor: Any) -> dict[str, Any]:
    """One of tinker's ``TensorData`` arrays as a wire tensor.

    ``dtype`` is required: the server rejects an unset one outright, since a tensor whose
    element type it had to guess could be silently reinterpreted.
    """
    if tensor.dtype not in _WIRE_DTYPE:
        msg = f"Together supports {sorted(_WIRE_DTYPE)} tensors only, got {tensor.dtype!r}"
        raise ValueError(msg)
    return {"data": tensor.tolist(), "dtype": _WIRE_DTYPE[tensor.dtype]}


def _to_sample(datum: types.Datum, loss_inputs_key: str) -> WireSample:
    arrays = {key: _to_tensor(value) for key, value in datum.loss_fn_inputs.items()}
    # `weights` stays omitted, like tinker's Datum: advantages of 0.0 already mask the
    # prompt positions, so gradients match exactly; only per-token KL/entropy diagnostics
    # count prompt tokens as active and read slightly diluted.
    loss_inputs = cast(
        "LossInputs",
        {
            "target_tokens": arrays["target_tokens"],
            loss_inputs_key: {
                "logprobs": arrays["logprobs"],
                "advantages": arrays["advantages"],
            },
        },
    )
    return WireSample(
        model_input=_to_model_input(datum.model_input),
        loss_inputs=loss_inputs,
        policy_segments=[],
    )


# The losses whose wire inputs are exactly the {logprobs, advantages} pair that
# _to_sample builds. cross_entropy Datums carry weights instead, and cispo/dro
# Datums carry extra keys the conversion would silently drop.
_ADVANTAGE_LOSSES = {"grpo", "importance_sampling", "ppo"}


def _loss_inputs_key(proto_loss_type: str) -> str:
    loss = proto_loss_type.removeprefix("LOSS_TYPE_").lower()
    if loss not in _ADVANTAGE_LOSSES:
        msg = f"the tinker wrapper supports loss_fn {sorted(_ADVANTAGE_LOSSES)} only, got {loss!r}"
        raise ValueError(msg)
    return loss + "_inputs"


def _stop_strings(stop: str | Sequence[str] | Sequence[int]) -> list[str]:
    """Keep the string stops; drop token-id ones, which the wire cannot carry.

    ``tinker_cookbook``'s renderers report their stops as token ids (Qwen3.5 gives
    ``[248046]``, i.e. ``<|im_end|>``), and those are the model's EOS, which the
    generator already stops on. Warn rather than raise: refusing them would mean a
    tinker script cannot pass its renderer's stops through unchanged.
    """
    if isinstance(stop, str):
        return [stop]
    strings = [item for item in stop if isinstance(item, str)]
    token_ids = [item for item in stop if not isinstance(item, str)]
    if token_ids:
        warnings.warn(
            f"Together's sampling stop takes strings only; ignoring token-id stops {token_ids}."
            " Generation still stops at the model's EOS token.",
            stacklevel=4,  # _stop_strings -> _to_sampling_params -> sample -> caller
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


def _to_sample_response(result: SampleResult) -> types.SampleResponse:
    return types.SampleResponse(
        sequences=[
            types.SampledSequence(
                stop_reason=_STOP_REASON[sequence.stop_reason],
                # int64 tokens arrive as strings on the wire
                tokens_np=np.asarray([int(token) for token in sequence.tokens], dtype=np.int64),
                logprobs_np=None if sequence.logprobs is None else np.asarray(sequence.logprobs, dtype=np.float32),
            )
            for sequence in result.sequences
        ]
    )
