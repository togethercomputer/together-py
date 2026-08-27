"""Coercion of torch/numpy arrays in native RL requests into their JSON wire shape.

The wire types are TypedDicts, so they cannot coerce their own members the way tinker's
``Datum`` does in ``__post_init__``. The native submitters call these helpers instead,
before validation and serialization, so a caller can write
``Sample(loss_fn_inputs={"target_tokens": torch.tensor(...)})`` and have it reach the
server as ``{"data": [...], "dtype": "int64"}``.

Arrays are recognized by duck typing rather than ``isinstance``: torch and numpy are both
optional dependencies, and a caller who passes plain lists should not pull either import in.
"""

from __future__ import annotations

from typing import Any, cast
from collections.abc import Mapping, Iterable, Sequence
from typing_extensions import Literal, TypeAlias

from ._losses import INPUT_DTYPES
from ._request_types import Sample
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.tensor_data_param import TensorData
from ....types.beta.rl.operation_custom_forward_backward_params import Gradient

WireDtype: TypeAlias = Literal["int64", "float32"]

_KIND_DTYPES: Mapping[str, WireDtype] = {"f": "float32", "i": "int64", "u": "int64", "b": "int64"}
_INTEGER_KINDS = frozenset({"i", "u", "b"})


def _to_array(value: object) -> Any | None:
    """Return ``value`` as a numpy array, or ``None`` when it is not an array at all.

    Torch tensors are detached, moved to the host, and widened out of any float narrower
    than ``float32`` — numpy cannot represent ``bfloat16``, and ``float32`` is the only
    float the wire carries.
    """
    if isinstance(value, (str, bytes, list, tuple)) or not hasattr(value, "tolist"):
        return None
    detach = getattr(value, "detach", None)
    if detach is None:  # numpy, or anything else exposing the array protocol we use
        return value
    tensor = detach().cpu()
    return (tensor.float() if tensor.dtype.is_floating_point else tensor).numpy()


def _to_wire_list(array: Any, label: str) -> list[Any]:
    """Flatten a one-dimensional array into JSON numbers, rejecting any other rank."""
    if array.ndim != 1:
        raise ValueError(
            f"{label} is {array.ndim}-dimensional, but training operations accept one-dimensional"
            " dense tensors only; flatten it before submitting."
        )
    return cast("list[Any]", array.tolist())


def _list_dtype(key: str, values: Sequence[object]) -> WireDtype:
    """Infer a wire dtype for a plain list, preferring the one its key pins."""
    if not all(isinstance(value, (int, float)) for value in values):
        raise ValueError(
            f"loss_fn_inputs[{key!r}] must be a flat numeric list; flatten a nested one, or pass"
            " a torch/numpy array or a TensorData with an explicit dtype instead."
        )
    allowed = INPUT_DTYPES.get(key)
    if allowed is not None and len(allowed) == 1:
        return cast("WireDtype", next(iter(allowed)))
    return "int64" if all(isinstance(value, int) for value in values) else "float32"


def _coerce_tensor(key: str, value: object) -> TensorData:
    """Convert one ``loss_fn_inputs`` value into a wire tensor, unchanged when already one."""
    label = f"loss_fn_inputs[{key!r}]"
    if isinstance(value, Mapping):
        tensor = cast("Mapping[str, Any]", value)
        array = _to_array(tensor.get("data"))
        if array is None:
            return cast("TensorData", value)
        # The declared dtype stands: the caller spelled it out, and validate_sample checks it.
        return cast("TensorData", {**tensor, "data": _to_wire_list(array, f"{label}['data']")})

    array = _to_array(value)
    if array is not None:
        # An array keeps its own dtype, as tinker's does, so an integer `advantages` array
        # fails the pinned-dtype check rather than being silently widened.
        dtype = _KIND_DTYPES.get(array.dtype.kind)
        if dtype is None:
            raise ValueError(f"{label} has unsupported dtype {array.dtype}; use an integer or float array.")
        return {"data": _to_wire_list(array, label), "dtype": dtype}

    if isinstance(value, (list, tuple)):
        values = cast("Sequence[object]", value)
        return {"data": cast("list[float]", list(values)), "dtype": _list_dtype(key, values)}

    raise TypeError(
        f"{label} must be a TensorData mapping, a torch/numpy array, or a numeric list, got {type(value).__name__}."
    )


def _coerce_chunk(chunk: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """Convert one input chunk's token array, or return ``None`` when it holds no array."""
    encoded_text = chunk.get("encoded_text")
    if not isinstance(encoded_text, Mapping):
        return None
    encoded = cast("Mapping[str, Any]", encoded_text)
    array = _to_array(encoded.get("tokens"))
    if array is None:
        return None
    if array.dtype.kind not in _INTEGER_KINDS:
        raise ValueError(f"Model input tokens must be an integer array, got {array.dtype}.")
    tokens = _to_wire_list(array, "model_input token chunk")
    return {**chunk, "encoded_text": {**encoded, "tokens": tokens}}


def coerce_model_input(model_input: ModelInput) -> ModelInput:
    """Convert torch/numpy token arrays in a model input into JSON integer lists."""
    mapping = cast("Mapping[str, Any]", model_input)
    # `chunks` is typed as an Iterable, so it is materialized before being walked twice.
    given = mapping.get("chunks", ())
    chunks = list(cast("Iterable[Any]", given))
    coerced = [_coerce_chunk(cast("Mapping[str, Any]", chunk)) for chunk in chunks]
    if isinstance(given, Sequence) and all(chunk is None for chunk in coerced):
        return model_input
    merged = [chunk if coerced_chunk is None else coerced_chunk for coerced_chunk, chunk in zip(coerced, chunks)]
    return cast("ModelInput", {**mapping, "chunks": merged})


def coerce_sample(sample: Sample) -> Sample:
    """Convert a sample's torch/numpy tensors and prompt tokens into their JSON wire shape.

    The sample is returned unchanged when it already holds nothing but JSON-ready values,
    so a caller reusing one sample dict across steps keeps their own object; otherwise a
    copy is returned and the caller's dict is left alone.
    """
    mapping = cast("Mapping[str, Any]", sample)
    inputs = mapping.get("loss_fn_inputs")
    if not isinstance(inputs, Mapping):
        return sample  # left to validate_sample, whose message names the offending field
    typed_inputs = cast("Mapping[str, Any]", inputs)
    coerced = {key: _coerce_tensor(key, value) for key, value in typed_inputs.items()}

    model_input = mapping.get("model_input")
    coerced_input = (
        coerce_model_input(cast("ModelInput", model_input)) if isinstance(model_input, Mapping) else model_input
    )
    if coerced_input is model_input and all(coerced[key] is value for key, value in typed_inputs.items()):
        return sample

    updated: dict[str, Any] = {**mapping, "loss_fn_inputs": coerced}
    if coerced_input is not model_input:
        updated["model_input"] = coerced_input
    return cast("Sample", updated)


def coerce_gradient(gradient: Gradient) -> Gradient:
    """Convert a custom-gradient's torch/numpy ``data`` into JSON numbers.

    ``dtype`` is left exactly as the caller set it: gradients still carry the older
    ``D_TYPE_*`` enum rather than the lowercase tensor dtype, and the server defaults it.
    """
    mapping = cast("Mapping[str, Any]", gradient)
    array = _to_array(mapping.get("data"))
    if array is None:
        return gradient
    return cast("Gradient", {**mapping, "data": _to_wire_list(array, "Gradient.data")})
