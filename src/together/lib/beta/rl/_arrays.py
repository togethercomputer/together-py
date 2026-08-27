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

import numbers
from typing import Any, cast
from collections.abc import Mapping, Iterable, Sequence
from typing_extensions import Literal, TypeAlias

from ._losses import INPUT_DTYPES
from ._request_types import Sample
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.tensor_data_param import TensorData
from ....types.beta.rl.operation_custom_forward_backward_params import Gradient

_WireDtype: TypeAlias = Literal["int64", "float32"]

_KIND_DTYPES: Mapping[str, _WireDtype] = {"f": "float32", "i": "int64", "u": "int64"}
_NUMPY_DTYPES: Mapping[str, str] = {"int64": "int64", "float32": "float32"}


def _to_array(value: object) -> Any | None:
    """Return ``value`` as an array ready to serialize, or ``None`` when it is not an array.

    Recognized by the attributes actually used downstream, so anything else falls through
    to the caller's own error rather than an ``AttributeError`` from deep inside here.
    Torch tensors are detached and moved to the host, and floats narrower than ``float32``
    (``bfloat16`` above all) widen — numpy cannot represent them, and ``float32`` is the
    only float the wire carries. Booleans become integers, since JSON would otherwise
    render them as ``true``/``false`` under an ``int64`` dtype.
    """
    if not (hasattr(value, "ndim") and hasattr(value, "dtype") and hasattr(value, "tolist")):
        return None
    detach = getattr(value, "detach", None)
    if detach is not None:  # a torch tensor; numpy arrays have no autograd graph or device
        tensor = detach().cpu()
        value = (tensor.float() if tensor.dtype.is_floating_point else tensor).numpy()
    array = cast(Any, value)
    return array.astype("int64") if array.dtype.kind == "b" else array


def _to_wire_list(array: Any, label: str) -> list[Any]:
    """Convert a one-dimensional array into JSON numbers, rejecting any other rank."""
    if array.ndim != 1:
        raise ValueError(
            f"{label} is {array.ndim}-dimensional, but training operations accept one-dimensional"
            " dense tensors only; flatten it before submitting."
        )
    return cast("list[Any]", array.tolist())


def _list_dtype(key: str, values: Sequence[object]) -> _WireDtype:
    """Infer a wire dtype for a plain list of numbers.

    A key with a single accepted dtype pins it, so ``advantages=[0, 1]`` is ``float32``
    the way tinker's key table has it. Floating-point values override that pin rather than
    being relabeled as integers: the resulting dtype is what ``validate_sample`` rejects,
    which names the offending key and its accepted dtypes.

    Raises:
        ValueError: If ``values`` holds anything that is not a real number.
    """
    if not all(isinstance(value, numbers.Real) for value in values):
        raise ValueError(
            f"loss_fn_inputs[{key!r}] must be a flat list of numbers; flatten a nested one, or pass"
            " a torch/numpy array or a TensorData with an explicit dtype instead."
        )
    if any(not isinstance(value, numbers.Integral) for value in values):
        return "float32"
    allowed = INPUT_DTYPES.get(key)
    if allowed is not None and len(allowed) == 1:
        return cast("_WireDtype", next(iter(allowed)))
    return "int64"


def _to_json_numbers(values: Sequence[Any]) -> list[Any]:
    """Narrow a numeric list onto the plain ints and floats ``json`` can encode."""
    return [int(value) if isinstance(value, numbers.Integral) else float(value) for value in values]


def _coerce_tensor(key: str, value: object) -> TensorData:
    """Convert one ``loss_fn_inputs`` value into a wire tensor.

    Raises:
        ValueError: If the value is not a tensor mapping, an array, or a numeric list, or
            if it is an array this shape cannot carry.
    """
    label = f"loss_fn_inputs[{key!r}]"
    if isinstance(value, Mapping):
        tensor = cast("Mapping[str, Any]", value)
        array = _to_array(tensor.get("data"))
        if array is None:
            return cast("TensorData", value)
        # Cast to the dtype the caller declared, as tinker's TensorData does, so `data` and
        # `dtype` cannot contradict each other on the wire.
        numpy_dtype = _NUMPY_DTYPES.get(cast(str, tensor.get("dtype")))
        if numpy_dtype is not None:
            array = array.astype(numpy_dtype)
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
        values = cast("Sequence[Any]", value)
        dtype = _list_dtype(key, values)  # rejects non-numbers before they reach _to_json_numbers
        return {"data": _to_json_numbers(values), "dtype": dtype}

    raise ValueError(
        f"{label} must be a TensorData mapping, a torch/numpy array, or a numeric list, got {type(value).__name__}."
    )


def _coerce_chunk(chunk: Mapping[str, Any]) -> Mapping[str, Any]:
    """Convert one input chunk's token array into a JSON integer list.

    Raises:
        ValueError: If the tokens are a non-integer array.
    """
    encoded_text = chunk.get("encoded_text")
    if not isinstance(encoded_text, Mapping):
        return chunk
    encoded = cast("Mapping[str, Any]", encoded_text)
    array = _to_array(encoded.get("tokens"))
    if array is None:
        return chunk
    if array.dtype.kind not in ("i", "u"):
        raise ValueError(f"Model input tokens must be an integer array, got {array.dtype}.")
    tokens = _to_wire_list(array, "model_input token chunk")
    return {**chunk, "encoded_text": {**encoded, "tokens": tokens}}


def coerce_model_input(model_input: ModelInput) -> ModelInput:
    """Convert torch/numpy token arrays in a model input into JSON integer lists."""
    mapping = cast("Mapping[str, Any]", model_input)
    given = mapping.get("chunks")
    if given is None:
        return model_input
    chunks = [_coerce_chunk(cast("Mapping[str, Any]", chunk)) for chunk in cast("Iterable[Any]", given)]
    return cast("ModelInput", {**mapping, "chunks": chunks})


def coerce_sample(sample: Sample) -> Sample:
    """Convert a sample's torch/numpy tensors and prompt tokens into their JSON wire shape.

    Copies on write at every level, so a caller reusing one sample dict across steps never
    sees its own tensors replaced.
    """
    mapping = cast("Mapping[str, Any]", sample)
    inputs = mapping.get("loss_fn_inputs")
    if not isinstance(inputs, Mapping):
        return sample  # left to validate_sample, whose message names the offending field
    typed_inputs = cast("Mapping[str, Any]", inputs)
    updated: dict[str, Any] = {
        **mapping,
        "loss_fn_inputs": {key: _coerce_tensor(key, value) for key, value in typed_inputs.items()},
    }
    model_input = mapping.get("model_input")
    if isinstance(model_input, Mapping):
        updated["model_input"] = coerce_model_input(cast("ModelInput", model_input))
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
