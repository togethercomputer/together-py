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

_WireDtype: TypeAlias = Literal["int64", "float32"]

_KIND_DTYPES: Mapping[str, _WireDtype] = {"f": "float32", "i": "int64", "u": "int64"}
_TOKEN_LABEL = "model_input token chunk"


def _to_array(value: object) -> Any | None:
    """Return ``value`` as a numpy array ready to serialize, or ``None`` if it is not an array.

    Torch tensors are detached and moved to the host, and every float tensor becomes
    ``float32`` — the only float the wire carries, and the only one numpy can take a
    ``bfloat16`` to. Boolean arrays become integers, since JSON would otherwise render
    them as ``true``/``false`` under an ``int64`` dtype.
    """
    if not (hasattr(value, "ndim") and hasattr(value, "dtype") and hasattr(value, "tolist")):
        return None
    detach = getattr(value, "detach", None)
    if detach is not None:  # A torch tensor; numpy arrays have no autograd graph or device.
        tensor = detach().cpu()
        value = (tensor.float() if tensor.dtype.is_floating_point else tensor).numpy()
    array = cast(Any, value)
    return array.astype("int64") if array.dtype.kind == "b" else array


def _to_wire_list(array: Any, label: str) -> list[Any]:
    """Convert a one-dimensional array into JSON numbers.

    Raises:
        ValueError: If the array is not one-dimensional.
    """
    if array.ndim != 1:
        raise ValueError(
            f"{label} is {array.ndim}-dimensional, but training operations accept one-dimensional"
            " dense tensors only; flatten it before submitting."
        )
    return cast(list[Any], array.tolist())


def _to_json_number(value: Any, label: str) -> int | float:
    """Narrow one element onto the plain ``int`` or ``float`` that ``json`` can encode.

    Raises:
        ValueError: If the element is not a number, which a nested list is the usual cause of.
    """
    item = getattr(value, "item", None)  # Every numpy and torch scalar has one; native numbers do not.
    scalar = item() if item is not None else value
    if isinstance(scalar, bool):  # JSON would otherwise render it as true/false under an integer dtype.
        return int(scalar)
    if isinstance(scalar, (int, float)):
        return scalar
    raise ValueError(
        f"{label} must be a flat list of numbers; flatten a nested one, or pass a torch/numpy array instead."
    )


def _to_json_numbers(values: Sequence[Any], label: str) -> list[Any]:
    """Narrow a numeric sequence onto the numbers ``json`` can encode."""
    return [_to_json_number(value, label) for value in values]


def _list_dtype(key: str, values: Sequence[Any]) -> _WireDtype:
    """Pick a wire dtype for an already-narrowed list of numbers.

    A key with a single accepted dtype pins it, so ``advantages=[0, 1]`` is ``float32``
    the way tinker's key table has it. Floating-point values override that pin rather than
    being relabeled as integers: the resulting dtype is what ``validate_sample`` rejects,
    which names the offending key and its accepted dtypes.
    """
    if any(isinstance(value, float) for value in values):
        return "float32"
    allowed = INPUT_DTYPES.get(key)
    if allowed is not None and len(allowed) == 1:
        return cast(_WireDtype, next(iter(allowed)))
    return "int64"


def _cast_to_declared(array: Any, declared: _WireDtype, label: str) -> Any:
    """Align an array with the dtype its own tensor mapping declares.

    Widening is silent, the way tinker's ``TensorData`` does it; truncating is not, since
    rounding ``1.5`` to ``1`` under a declared ``int64`` would corrupt token IDs with no signal.

    Raises:
        ValueError: If the declared dtype cannot hold the array's values.
    """
    if declared == "int64" and array.dtype.kind == "f":
        raise ValueError(
            f"{label} holds floating-point values but declares dtype 'int64'; cast the array"
            " yourself if truncation is intended, or declare 'float32'."
        )
    return array.astype(declared)


def _coerce_tensor(key: str, value: object) -> TensorData:
    """Convert one ``loss_fn_inputs`` value into a wire tensor.

    Raises:
        ValueError: If the value is not a tensor mapping, an array, or a numeric list, or
            if it is an array this shape cannot carry.
    """
    label = f"loss_fn_inputs[{key!r}]"
    if isinstance(value, Mapping):
        tensor = cast(Mapping[str, Any], value)
        data = tensor.get("data")
        array = _to_array(data)
        if array is None:
            if not isinstance(data, (list, tuple)):
                return cast(TensorData, value)
            values = cast(Sequence[Any], data)
            return cast(TensorData, {**tensor, "data": _to_json_numbers(values, f"{label}['data']")})
        declared = tensor.get("dtype")
        if declared in ("int64", "float32"):
            array = _cast_to_declared(array, declared, f"{label}['data']")
        return cast(TensorData, {**tensor, "data": _to_wire_list(array, f"{label}['data']")})

    array = _to_array(value)
    if array is not None:
        # An array keeps its own dtype, as tinker's does, so an integer `advantages` array
        # fails the pinned-dtype check rather than being silently widened.
        dtype = _KIND_DTYPES.get(array.dtype.kind)
        if dtype is None:
            raise ValueError(f"{label} has unsupported dtype {array.dtype}; use an integer or float array.")
        return {"data": _to_wire_list(array, label), "dtype": dtype}

    if isinstance(value, (list, tuple)):
        data = _to_json_numbers(cast(Sequence[Any], value), label)
        return {"data": data, "dtype": _list_dtype(key, data)}

    raise ValueError(
        f"{label} must be a TensorData mapping, a torch/numpy array, or a numeric list, got {type(value).__name__}."
    )


def _coerce_chunk(chunk: Mapping[str, Any]) -> Mapping[str, Any]:
    """Convert one input chunk's tokens into a JSON integer list.

    Raises:
        ValueError: If the tokens are a non-integer array, or hold anything but numbers.
    """
    encoded_text = chunk.get("encoded_text")
    if not isinstance(encoded_text, Mapping):
        return chunk
    encoded = cast(Mapping[str, Any], encoded_text)
    given = encoded.get("tokens")
    array = _to_array(given)
    if array is not None:
        if array.dtype.kind not in ("i", "u"):
            raise ValueError(f"{_TOKEN_LABEL} must be an integer array, got {array.dtype}.")
        tokens = _to_wire_list(array, _TOKEN_LABEL)
    elif isinstance(given, (list, tuple)):
        tokens = _to_json_numbers(cast(Sequence[Any], given), _TOKEN_LABEL)
    else:
        return chunk
    return {**chunk, "encoded_text": {**encoded, "tokens": tokens}}


def coerce_model_input(model_input: ModelInput) -> ModelInput:
    """Convert torch/numpy token arrays in a model input into JSON integer lists."""
    mapping = cast(Mapping[str, Any], model_input)
    given = mapping.get("chunks")
    if given is None:
        return model_input
    chunks = [_coerce_chunk(cast(Mapping[str, Any], chunk)) for chunk in cast(Iterable[Any], given)]
    return cast(ModelInput, {**mapping, "chunks": chunks})


def coerce_sample(sample: Sample) -> Sample:
    """Convert a sample's torch/numpy tensors and prompt tokens into their JSON wire shape.

    Copies on write at every level, so a caller reusing one sample dict across steps never
    sees its own tensors replaced.
    """
    mapping = cast(Mapping[str, Any], sample)
    inputs = mapping.get("loss_fn_inputs")
    if not isinstance(inputs, Mapping):
        return sample  # Left to validate_sample, whose message names the offending field.
    typed_inputs = cast(Mapping[str, Any], inputs)
    updated: dict[str, Any] = {
        **mapping,
        "loss_fn_inputs": {key: _coerce_tensor(key, value) for key, value in typed_inputs.items()},
    }
    model_input = mapping.get("model_input")
    if isinstance(model_input, Mapping):
        updated["model_input"] = coerce_model_input(cast(ModelInput, model_input))
    return cast(Sample, updated)


def coerce_gradient(gradient: Gradient) -> Gradient:
    """Convert a custom-gradient's torch/numpy ``data`` into JSON numbers.

    ``dtype`` is left exactly as the caller set it: gradients still carry the older
    ``D_TYPE_*`` enum rather than the lowercase tensor dtype, and the server defaults it.
    """
    mapping = cast(Mapping[str, Any], gradient)
    given = mapping.get("data")
    array = _to_array(given)
    if array is not None:
        data = _to_wire_list(array, "Gradient.data")
    elif isinstance(given, (list, tuple)):
        data = _to_json_numbers(cast(Sequence[Any], given), "Gradient.data")
    else:
        return gradient
    return cast(Gradient, {**mapping, "data": data})
