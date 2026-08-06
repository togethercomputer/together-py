"""Pure conversions between tinker types and Together's RL wire types."""

from __future__ import annotations

import warnings
from typing import Any, Literal, Sequence, cast

import numpy as np
from tinker.types.topk_prompt_logprobs import TopkPromptLogprobs

from .. import (
    Sample as WireSample,
    AdamParams as WireAdamParams,
    LossInputs,
    SampleResult,
    SamplingParams as WireSamplingParams,
    ForwardBackwardResult,
)
from ._compat import types
from .....types.beta.rl.model_input_param import ModelInput as WireModelInput
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
    required = ("target_tokens", "logprobs", "advantages")
    inputs = datum.loss_fn_inputs
    if set(inputs) != set(required):
        raise ValueError(
            f"Datum.loss_fn_inputs keys {sorted(inputs)} != expected {list(required)}"
        )
    arrays = {key: _to_tensor(inputs[key]) for key in required}
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
    )


# Losses whose Datum.loss_fn_inputs are exactly {target_tokens, logprobs, advantages}.
# cross_entropy carries weights instead; cispo/dro carry extra keys — both fail in
# _loss_inputs_key / _to_sample rather than silently dropping fields.
# grpo is a Together wire loss, not a tinker LossFnType, so it is not listed here.
_ADVANTAGE_LOSSES = frozenset({"importance_sampling", "ppo"})


def _loss_inputs_key(loss_fn: str) -> str:
    loss = loss_fn.removeprefix("LOSS_TYPE_").lower()
    if loss not in _ADVANTAGE_LOSSES:
        msg = f"the tinker wrapper supports loss_fn {sorted(_ADVANTAGE_LOSSES)} only, got {loss!r}"
        raise ValueError(msg)
    return f"{loss}_inputs"


def _to_forward_backward_output(result: ForwardBackwardResult) -> types.ForwardBackwardOutput:
    """Map Together's scalar loss + metrics onto tinker's ForwardBackwardOutput.

    Per-datum ``loss_fn_outputs`` are left empty: Together does not return them, and
    inventing logprobs would silently corrupt scripts that read them. Scripts that only
    read ``.metrics`` (including tinker's ``loss:sum``) keep working because Together's
    total ``loss`` is published under that key.
    """
    metrics = dict(result.metrics or {})
    metrics.setdefault("loss:sum", result.loss)
    return types.ForwardBackwardOutput(
        loss_fn_output_type="",
        loss_fn_outputs=[],
        metrics=metrics,
    )


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
