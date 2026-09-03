"""Coercion of torch/numpy arrays in native RL requests into their JSON wire shape.

The wire types are TypedDicts, so they cannot coerce their own members the way tinker's
``Datum`` does in ``__post_init__``. The native submitters call these helpers instead,
before validation and serialization, so a caller can write
``Sample(loss_fn_inputs={"target_tokens": torch.tensor(...)})`` and have it reach the
server as ``{"data": [...], "dtype": "int64"}``.

Arrays are recognized by duck typing rather than ``isinstance``: torch and numpy are both
optional dependencies, and a caller who passes plain lists should not pull either import in.

Every helper takes a ``label`` naming the field it is working on, so an error out of a
256-sample batch says which sample and which key it came from.
"""

from __future__ import annotations

import math
import types
from typing import Any, cast
from dataclasses import dataclass
from collections.abc import Mapping, Iterable, Sequence
from typing_extensions import Literal, TypeAlias

from ._losses import INPUT_DTYPES
from ._request_types import Sample
from ....types.beta.rl.model_input_param import ModelInput
from ....types.beta.rl.tensor_data_param import TensorDataParam as TensorData
from ....types.beta.rl.operation_custom_forward_backward_params import Gradient

_WireDtype: TypeAlias = Literal["int64", "float32"]

_KIND_DTYPES: Mapping[str, _WireDtype] = types.MappingProxyType({"f": "float32", "i": "int64", "u": "int64"})
_NUMPY_FLOATS = frozenset({"torch.float16", "torch.float32", "torch.float64"})
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1
_FLOAT32_MAX = 3.4028234663852886e38


def _require_wire_range(numbers: Sequence[int | float], dtype: _WireDtype, label: str) -> None:
    """Reject finite values the declared wire dtype cannot hold.

    Non-finite floats are left for ``prepare_operation_body``, which names them as NaN/inf.
    """
    if dtype == "int64":
        if any(number < _INT64_MIN or number > _INT64_MAX for number in numbers):
            raise ValueError(f"{label} holds values outside signed int64; cast them or use a signed integer dtype.")
        return
    if any(
        abs(number) > _FLOAT32_MAX and (not isinstance(number, float) or math.isfinite(number)) for number in numbers
    ):
        raise ValueError(f"{label} holds values outside float32; the wire type is float32.")


def _widened(tensor: Any) -> Any:
    """Widen a float torch tensor to ``float32`` unless numpy can hold its dtype as it is.

    ``bfloat16`` is the case that matters, since numpy cannot hold it at all. Widening a
    dtype numpy already holds would round-trip its values instead, inflating every number
    on the wire. Tested by name rather than by ``dtype.itemsize``, which torch only grew
    in 2.1 — an older torch would otherwise fall back to widening everything.
    """
    return tensor if str(tensor.dtype) in _NUMPY_FLOATS else tensor.float()


@dataclass(frozen=True)
class _HostArray:
    """A 1-D numeric buffer with the numpy attributes the rest of this module reads."""

    data: tuple[int | float, ...]
    kind: str
    ndim: int

    @property
    def dtype(self) -> Any:
        return types.SimpleNamespace(kind=self.kind, char="")

    def astype(self, name: str) -> _HostArray:
        if name == "int64":
            return _HostArray(tuple(int(value) for value in self.data), "i", self.ndim)
        if name in ("float32", "float64"):
            return _HostArray(tuple(float(value) for value in self.data), "f", self.ndim)
        return self

    def tolist(self) -> list[int | float]:
        return list(self.data)


def _torch_kind(dtype: Any) -> str:
    name = str(dtype)
    if name == "torch.bool":
        return "b"
    if "uint" in name:
        return "u"
    if "int" in name:
        return "i"
    return "f"


def _host_array_from_torch(tensor: Any) -> _HostArray:
    values = tensor.tolist()
    kind = _torch_kind(tensor.dtype)
    if kind == "b":
        values = [int(value) for value in values]
        kind = "i"
    return _HostArray(tuple(values), kind, int(getattr(tensor, "ndim", 1)))


def _to_array(value: object, label: str) -> Any:
    """Return ``value`` as a numpy array ready to serialize, or ``None`` if it is not an array.

    Torch tensors are detached and moved to the host, converted through ``tolist`` so
    numpy need not be installed, and a float dtype numpy cannot hold (``bfloat16`` above
    all) widens to ``float32`` first. Boolean arrays become integers, since JSON would
    otherwise render them as ``true``/``false`` under an ``int64`` dtype, and
    ``longdouble`` narrows to ``float64``, the widest float ``json`` can encode.

    Raises:
        ValueError: If the value is a sparse tensor or holds a dtype the wire cannot carry.
    """
    if not (hasattr(value, "ndim") and hasattr(value, "dtype") and hasattr(value, "tolist")):
        return None
    detach = getattr(value, "detach", None)
    if detach is not None:  # A torch tensor; numpy arrays have no autograd graph or device.
        # Every sparse layout, not just COO and CSR.
        if str(getattr(value, "layout", "torch.strided")) != "torch.strided":
            raise ValueError(
                f"{label} is a sparse tensor, but training operations accept dense tensors only;"
                " call .to_dense() before submitting."
            )
        tensor = detach().cpu()
        if tensor.dtype.is_floating_point:
            tensor = _widened(tensor)
        value = _host_array_from_torch(tensor)
    array = cast(Any, value)
    if array.dtype.kind == "b":  # numpy boolean
        array = array.astype("int64")
    if array.dtype.char == "g":  # numpy longdouble; width and name vary by platform
        # The one float whose tolist() hands back numpy scalars rather than native floats.
        array = array.astype("float64")
    if array.dtype.kind not in _KIND_DTYPES:
        raise ValueError(f"{label} has unsupported dtype {array.dtype}; use an integer or float array.")
    return array


def _to_wire_list(array: Any, label: str) -> list[int | float]:
    """Convert a one-dimensional array into JSON numbers.

    Raises:
        ValueError: If the array is not one-dimensional.
    """
    if array.ndim != 1:
        raise ValueError(
            f"{label} is {array.ndim}-dimensional, but training operations accept one-dimensional"
            " dense tensors only; reshape it to one dimension before submitting."
        )
    return cast("list[int | float]", array.tolist())


def _to_json_number(value: Any, label: str) -> int | float:
    """Narrow one element onto the plain ``int`` or ``float`` that ``json`` can encode.

    Raises:
        ValueError: If the element is not a number, which a nested list is the usual cause of.
    """
    # Exact types on purpose: `isinstance` would let `bool` through, and JSON renders a bool
    # as true/false where an integer dtype needs 1/0.
    if type(value) is int or type(value) is float:
        return value  # The common case, and the only one that needs no work at all.
    item = getattr(value, "item", None)  # Every numpy and torch scalar has one; native numbers do not.
    scalar = item() if item is not None else value
    if isinstance(scalar, bool):  # JSON would otherwise render it as true/false under an integer dtype.
        return int(scalar)
    if isinstance(scalar, (int, float)):
        return scalar
    raise ValueError(
        f"{label} must be a flat list of numbers; flatten a nested one, or pass a torch/numpy array instead."
    )


def _to_json_numbers(values: Sequence[Any], label: str) -> list[int | float]:
    """Narrow a numeric sequence onto the numbers ``json`` can encode."""
    return [_to_json_number(value, label) for value in values]


def _list_dtype(key: str, values: Sequence[int | float]) -> _WireDtype:
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


def _lossy_int64(label: str) -> ValueError:
    """Build the error for floating-point data under a declared ``int64`` dtype."""
    return ValueError(
        f"{label} holds floating-point values but declares dtype 'int64'; cast them"
        " yourself if truncation is intended, or declare 'float32'."
    )


def _cast_to_declared(array: Any, declared: _WireDtype, label: str) -> Any:
    """Align an array with the dtype its own tensor mapping declares.

    Widening is silent, the way tinker's ``TensorData`` does it; truncating is not, since
    rounding ``1.5`` to ``1`` under a declared ``int64`` would corrupt token IDs with no signal.

    Raises:
        ValueError: If the declared dtype cannot hold the array's values.
    """
    if declared == "int64" and array.dtype.kind == "f":
        raise _lossy_int64(label)
    # Widening integers is the only cast that changes a value. Sending a float array through
    # float32 would round-trip it instead, so 0.1 reaches the wire as 0.10000000149011612.
    return array.astype("float32") if declared == "float32" and array.dtype.kind != "f" else array


def _coerce_tensor(key: str, value: object, label: str) -> TensorData:
    """Convert one ``loss_fn_inputs`` value into a wire tensor.

    Raises:
        ValueError: If the value is not a tensor mapping, an array, or a numeric list, or
            if it is an array this shape cannot carry.
    """
    if isinstance(value, Mapping):
        tensor = cast(Mapping[str, Any], value)
        data = tensor.get("data")
        data_label = f"{label}['data']"
        array = _to_array(data, data_label)
        declared = tensor.get("dtype")
        if array is None:
            if not isinstance(data, (list, tuple)):
                return cast(TensorData, value)
            numbers = _to_json_numbers(cast(Sequence[Any], data), data_label)
            if declared == "int64" and any(isinstance(number, float) for number in numbers):
                raise _lossy_int64(data_label)
            wire = declared if declared in ("int64", "float32") else _list_dtype(key, numbers)
            _require_wire_range(numbers, wire, data_label)
            return cast(TensorData, {**tensor, "data": numbers})
        wire = declared if declared in ("int64", "float32") else _KIND_DTYPES[array.dtype.kind]
        if declared in ("int64", "float32"):
            array = _cast_to_declared(array, declared, data_label)
        numbers = _to_wire_list(array, data_label)
        _require_wire_range(numbers, wire, data_label)
        return cast(TensorData, {**tensor, "data": numbers})

    array = _to_array(value, label)
    if array is not None:
        # An array keeps its own dtype, as tinker's does, so an integer `advantages` array
        # fails the pinned-dtype check rather than being silently widened.
        dtype = _KIND_DTYPES[array.dtype.kind]
        numbers = _to_wire_list(array, label)
        _require_wire_range(numbers, dtype, label)
        return {"data": numbers, "dtype": dtype}

    if isinstance(value, (list, tuple)):
        numbers = _to_json_numbers(cast(Sequence[Any], value), label)
        dtype = _list_dtype(key, numbers)
        _require_wire_range(numbers, dtype, label)
        return {"data": numbers, "dtype": dtype}

    raise ValueError(
        f"{label} must be a TensorData mapping, a torch/numpy array, or a numeric list, got {type(value).__name__}."
    )


def _coerce_chunk(chunk: object, label: str) -> object:
    """Convert one input chunk's tokens into a JSON integer list.

    Raises:
        ValueError: If the tokens are not integers, or hold anything but numbers.
    """
    if not isinstance(chunk, Mapping):
        return chunk
    typed_chunk = cast(Mapping[str, Any], chunk)
    encoded_text = typed_chunk.get("encoded_text")
    if not isinstance(encoded_text, Mapping):
        return typed_chunk
    encoded = cast(Mapping[str, Any], encoded_text)
    raw_tokens = encoded.get("tokens")
    token_label = f"{label}.encoded_text.tokens"
    array = _to_array(raw_tokens, token_label)
    tokens: list[int | float | str]
    if array is not None:
        if array.dtype.kind not in ("i", "u"):
            raise ValueError(f"{token_label} must be an integer array, got {array.dtype}.")
        tokens = list(_to_wire_list(array, token_label))
    elif isinstance(raw_tokens, (list, tuple)):
        tokens = [
            token if type(token) is str else _to_json_number(token, token_label)
            for token in cast(Sequence[Any], raw_tokens)
        ]
        if any(isinstance(token, float) for token in tokens):
            raise ValueError(f"{token_label} must hold integers, but holds floating-point values.")
    else:
        return typed_chunk
    _require_wire_range([token for token in tokens if type(token) is int], "int64", token_label)
    return {**typed_chunk, "encoded_text": {**encoded, "tokens": tokens}}


def coerce_model_input(model_input: ModelInput, label: str = "model_input") -> ModelInput:
    """Convert torch/numpy token arrays in a model input into JSON integer lists."""
    mapping = cast(Mapping[str, Any], model_input)
    raw_chunks = mapping.get("chunks")
    if raw_chunks is None:
        return model_input
    chunks = [
        _coerce_chunk(chunk, f"{label}.chunks[{index}]") for index, chunk in enumerate(cast(Iterable[Any], raw_chunks))
    ]
    return cast(ModelInput, {**mapping, "chunks": chunks})


def coerce_sample(sample: Sample, label: str = "sample") -> Sample:
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
        "loss_fn_inputs": {
            key: _coerce_tensor(key, value, f"{label}.loss_fn_inputs[{key!r}]") for key, value in typed_inputs.items()
        },
    }
    model_input = mapping.get("model_input")
    if isinstance(model_input, Mapping):
        updated["model_input"] = coerce_model_input(cast(ModelInput, model_input), f"{label}.model_input")
    return cast(Sample, updated)


def coerce_gradient(gradient: Gradient, label: str = "gradient") -> Gradient:
    """Convert a custom-gradient's torch/numpy ``data`` into JSON numbers.

    ``dtype`` is left exactly as the caller set it: gradients still carry the older
    ``D_TYPE_*`` enum rather than the lowercase tensor dtype, and the server defaults it.
    """
    mapping = cast(Mapping[str, Any], gradient)
    raw_data = mapping.get("data")
    data_label = f"{label}.data"
    array = _to_array(raw_data, data_label)
    if array is not None:
        data = _to_wire_list(array, data_label)
    elif isinstance(raw_data, (list, tuple)):
        data = _to_json_numbers(cast(Sequence[Any], raw_data), data_label)
    else:
        return gradient
    _require_wire_range(data, "float32", data_label)
    return cast(Gradient, {**mapping, "data": data})
