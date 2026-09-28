"""Torch/numpy coercion on the native RL clients.

numpy is installed by the ``tinker`` extra, so the numpy cases run on the ``test-tinker``
CI job and skip elsewhere. torch is not installed anywhere in CI — nothing this package
ships depends on it — so the torch branch is covered by ``FakeTensor``, a stub that
enforces the parts of torch's contract the coercion relies on: ``.numpy()`` refuses a
tensor that still carries an autograd graph, lives off the host, or holds ``bfloat16``.
"""

from __future__ import annotations

import json
import array
from types import SimpleNamespace
from typing import Any, cast
from dataclasses import replace, dataclass
from collections.abc import Callable
from typing_extensions import override

import pytest

from tests.unit.rl_wait import patch_wait
from tests.unit._rl_fakes import FakeClient
from together.lib.beta.rl import (
    Sample,
    Gradient,
    LossConfig,
    ModelInput,
    TensorData,
    SampleResult,
    SessionClient,
    ModelInputChunk,
    EncodedTextChunk,
    ForwardBackwardResult,
)
from together.lib.beta.rl._arrays import coerce_sample, coerce_gradient, coerce_model_input


@pytest.fixture
def np() -> Any:
    return pytest.importorskip("numpy")


@dataclass(frozen=True)
class FakeDtype:
    """A torch dtype stand-in: the coercion reads it by name, as torch prints it."""

    name: str

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def is_floating_point(self) -> bool:
        return self.name.startswith(("torch.float", "torch.bfloat"))


@dataclass(frozen=True)
class FakeTensor:
    """A torch-shaped stand-in that fails the way a real tensor would."""

    values: Any
    dtype_name: str = "torch.int64"
    requires_grad: bool = False
    on_device: bool = False
    is_sparse: bool = False
    numpy_available: bool = True

    @property
    def layout(self) -> str:
        return "torch.sparse_coo" if self.is_sparse else "torch.strided"

    @property
    def dtype(self) -> FakeDtype:
        return FakeDtype(self.dtype_name)

    @property
    def ndim(self) -> int:
        return 1 if isinstance(self.values, list) else cast(int, self.values.ndim)

    def detach(self) -> FakeTensor:
        return replace(self, requires_grad=False)

    def cpu(self) -> FakeTensor:
        return replace(self, on_device=False)

    def float(self) -> FakeTensor:
        values = self.values
        if hasattr(values, "astype"):
            return replace(self, values=values.astype("float32"), dtype_name="torch.float32")
        return replace(self, values=[float(value) for value in values], dtype_name="torch.float32")

    def tolist(self) -> list[Any]:
        values = self.values
        if hasattr(values, "tolist"):
            return cast(list[Any], values.tolist())
        return list(values)

    def numpy(self) -> Any:
        if not self.numpy_available:
            raise RuntimeError("Numpy is not available")
        if self.requires_grad:
            raise RuntimeError("Can't call numpy() on Tensor that requires grad")
        if self.on_device:
            raise TypeError("can't convert a device tensor to numpy")
        if self.dtype_name == "torch.bfloat16":
            raise TypeError("Got unsupported ScalarType BFloat16")
        return self.values


def _model_input(tokens: Any) -> ModelInput:
    return ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=tokens))])


def _sample(loss_fn_inputs: Any, tokens: Any = (1, 2)) -> Sample:
    """Builds a ``Sample`` whose ``model_input`` has one token per ``loss_fn_inputs`` slot.

    Nothing in the coercion path compares the two, so pass ``tokens`` explicitly when the
    arrays under test are not two-valued.
    """
    return Sample(model_input=_model_input(list(tokens)), loss_fn_inputs=loss_fn_inputs)


def _last_kwargs(client: FakeClient) -> dict[str, Any]:
    assert client.beta.rl.operations.last_call is not None
    return client.beta.rl.operations.last_call[2]


def test_numpy_array_value_takes_the_array_dtype(np: Any) -> None:
    coerced = coerce_sample(_sample({"target_tokens": np.array([1, 2, 3], dtype=np.int32)}, tokens=(1, 2, 3)))

    assert coerced["loss_fn_inputs"] == {"target_tokens": {"data": [1, 2, 3], "dtype": "int64"}}


def _detached_device_tensor(np: Any) -> FakeTensor:
    """A float tensor still attached to the autograd graph and resident on a device."""
    return FakeTensor(
        np.array([0.5, -0.25], dtype=np.float64),
        dtype_name="torch.float64",
        requires_grad=True,
        on_device=True,
    )


_TENSOR_CASES: list[tuple[str, Callable[[Any], FakeTensor], dict[str, Any]]] = [
    (
        "advantages",
        _detached_device_tensor,
        {"data": [0.5, -0.25], "dtype": "float32"},
    ),
    (
        "advantages",
        lambda np: FakeTensor(np.array([1.0, 2.0], dtype=np.float32), dtype_name="torch.bfloat16"),
        {"data": [1.0, 2.0], "dtype": "float32"},
    ),
    (
        "target_tokens",
        lambda np: FakeTensor(np.array([7, 8], dtype=np.int64)),
        {"data": [7, 8], "dtype": "int64"},
    ),
    (
        "mask",
        lambda np: FakeTensor(np.array([True, False]), dtype_name="torch.bool"),
        {"data": [1, 0], "dtype": "int64"},
    ),
]


@pytest.mark.parametrize(
    ("key", "make_tensor", "expected"),
    _TENSOR_CASES,
    ids=["detached-and-moved-to-host", "bfloat16-widens", "integer-not-widened", "bool-becomes-int"],
)
def test_tensor_values_reach_the_wire_shape(
    np: Any, key: str, make_tensor: Callable[[Any], FakeTensor], expected: dict[str, Any]
) -> None:
    coerced = coerce_sample(_sample({key: make_tensor(np)}))

    assert coerced["loss_fn_inputs"][key] == expected


def test_array_data_keeps_its_declared_dtype(np: Any) -> None:
    tensor = TensorData(data=np.array([1, 2, 3], dtype=np.int64), dtype="int64")

    coerced = coerce_sample(_sample({"target_tokens": tensor}, tokens=(1, 2, 3)))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [1, 2, 3], "dtype": "int64"}


def test_lists_infer_the_dtype_their_key_pins() -> None:
    # `advantages` is float32 even though every value is an int, matching tinker's key table.
    coerced = coerce_sample(_sample({"target_tokens": [1, 2], "advantages": [0, 1]}))

    assert coerced["loss_fn_inputs"] == {
        "target_tokens": {"data": [1, 2], "dtype": "int64"},
        "advantages": {"data": [0, 1], "dtype": "float32"},
    }


def test_list_under_an_unknown_key_infers_from_its_values() -> None:
    coerced = coerce_sample(_sample({"target_tokens": [1], "future_input": [0.5]}, tokens=(1,)))

    assert coerced["loss_fn_inputs"]["future_input"] == {"data": [0.5], "dtype": "float32"}


def test_nested_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="flat list of numbers"):
        coerce_sample(_sample({"target_tokens": [[1, 2], [3, 4]]}))


def test_bool_list_becomes_integers(np: Any) -> None:
    """A Python bool and a numpy bool both narrow; neither may reach JSON as true/false."""
    coerced = coerce_sample(_sample({"mask": [True, np.bool_(False)]}))

    assert coerced["loss_fn_inputs"] == {"mask": {"data": [1, 0], "dtype": "int64"}}


def test_float_list_overrides_the_pinned_dtype() -> None:
    # int64 would contradict the data; float32 is what validate_sample rejects by name.
    coerced = coerce_sample(_sample({"target_tokens": [0.5, 1.5]}))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [0.5, 1.5], "dtype": "float32"}


def test_lossy_declared_dtype_is_rejected(np: Any) -> None:
    tensor = TensorData(data=np.array([1.5, 2.5], dtype=np.float32), dtype="int64")

    with pytest.raises(ValueError, match="declares dtype 'int64'"):
        coerce_sample(_sample({"target_tokens": tensor}))


def test_widening_declared_dtype_is_applied(np: Any) -> None:
    tensor = TensorData(data=np.array([1, 2], dtype=np.int64), dtype="float32")

    coerced = coerce_sample(_sample({"weights": tensor}))

    assert coerced["loss_fn_inputs"]["weights"] == {"data": [1.0, 2.0], "dtype": "float32"}


def test_numpy_scalars_in_declared_tensor_data_serialize(np: Any) -> None:
    tensor = TensorData(data=[np.float32(0.5), np.float32(1.5)], dtype="float32")

    coerced = coerce_sample(_sample({"advantages": tensor}))

    assert json.dumps(coerced["loss_fn_inputs"]["advantages"]["data"]) == "[0.5, 1.5]"


def test_json_ready_sample_keeps_its_values() -> None:
    sample = _sample({"target_tokens": TensorData(data=[1, 2], dtype="int64")})

    coerced = coerce_sample(sample)

    assert coerced["loss_fn_inputs"] == {"target_tokens": {"data": [1, 2], "dtype": "int64"}}
    assert coerced["model_input"] == sample["model_input"]


def test_caller_dict_is_not_mutated(np: Any) -> None:
    target_tokens = np.array([1, 2], dtype=np.int64)
    inputs: dict[str, Any] = {"target_tokens": target_tokens}
    sample = _sample(inputs)

    coerce_sample(sample)

    assert inputs["target_tokens"] is target_tokens


def test_multidimensional_array_is_rejected(np: Any) -> None:
    sample = _sample({"target_tokens": np.zeros((2, 2), dtype=np.int64)})

    with pytest.raises(ValueError, match="2-dimensional"):
        coerce_sample(sample)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(object(), id="arbitrary-object"),
        # Has `tolist`, but none of the array attributes the coercion needs; it must reach
        # the actionable error rather than an AttributeError from inside the array path.
        pytest.param(array.array("l", [1, 2]), id="stdlib-array"),
    ],
)
def test_unsupported_value_type_is_rejected(value: Any) -> None:
    with pytest.raises(ValueError, match="must be a TensorData mapping"):
        coerce_sample(_sample({"target_tokens": value}))


def test_float_token_array_is_rejected(np: Any) -> None:
    with pytest.raises(ValueError, match="must be an integer array"):
        coerce_model_input(_model_input(np.array([1.0, 2.0])))


def test_prompt_tokens_become_integers(np: Any) -> None:
    coerced = coerce_model_input(_model_input(FakeTensor(np.array([101, 102], dtype=np.int64))))

    assert coerced["chunks"][0]["encoded_text"]["tokens"] == [101, 102]  # type: ignore[index]


def test_gradient_data_keeps_its_proto_dtype(np: Any) -> None:
    gradient = Gradient(data=np.array([0.5, -0.5], dtype=np.float32), dtype="D_TYPE_FLOAT32")

    assert coerce_gradient(gradient) == {"data": [0.5, -0.5], "dtype": "D_TYPE_FLOAT32"}


def test_forward_backward_submits_serializable_arrays(monkeypatch: pytest.MonkeyPatch, np: Any) -> None:
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.trainer.forward_backward(
        samples=[
            Sample(
                model_input=_model_input(np.array([1, 2], dtype=np.int64)),
                loss_fn_inputs={
                    "target_tokens": np.array([1, 2], dtype=np.int64),
                    "logprobs": np.array([-0.5, -0.25], dtype=np.float32),
                    "advantages": np.array([1.0, 1.0], dtype=np.float32),
                },
            )
        ],
        loss=LossConfig(type="LOSS_TYPE_GRPO"),
    )

    kwargs = _last_kwargs(client)
    assert json.loads(json.dumps(kwargs["samples"])) == [
        {
            "model_input": {"chunks": [{"encoded_text": {"tokens": [1, 2]}}]},
            "loss_fn_inputs": {
                "target_tokens": {"data": [1, 2], "dtype": "int64"},
                "logprobs": {"data": [-0.5, -0.25], "dtype": "float32"},
                "advantages": {"data": [1.0, 1.0], "dtype": "float32"},
            },
        }
    ]
    session.stop()


def test_integer_advantages_array_fails_validation(monkeypatch: pytest.MonkeyPatch, np: Any) -> None:
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    session = SessionClient("sess", _client=cast(Any, FakeClient()))

    with pytest.raises(ValueError, match=r"advantages'\]\.dtype"):
        session.trainer.forward_backward(
            samples=[
                _sample(
                    {
                        "target_tokens": np.array([1, 2], dtype=np.int64),
                        "logprobs": np.array([-0.5, -0.25], dtype=np.float32),
                        "advantages": np.array([1, 1], dtype=np.int64),
                    }
                )
            ],
            loss=LossConfig(type="LOSS_TYPE_GRPO"),
        )
    session.stop()


def test_custom_forward_backward_serializes_gradient_arrays(monkeypatch: pytest.MonkeyPatch, np: Any) -> None:
    patch_wait(monkeypatch, SimpleNamespace(logprobs=[]))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.trainer.custom_forward_backward(
        samples=[_sample({"target_tokens": np.array([1, 2], dtype=np.int64)})],
        gradients=[Gradient(data=np.array([0.5, -0.5], dtype=np.float32))],
    )

    kwargs = _last_kwargs(client)
    assert json.loads(json.dumps(kwargs["gradients"])) == [{"data": [0.5, -0.5]}]
    session.stop()


def test_sample_batch_serializes_array_prompts(monkeypatch: pytest.MonkeyPatch, np: Any) -> None:
    patch_wait(monkeypatch, SimpleNamespace(results=[SampleResult(policy_segments=[], sequences=[])]))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.generator.sample_batch(prompts=[_model_input(np.array([7, 8], dtype=np.int32))])

    kwargs = _last_kwargs(client)
    assert json.loads(json.dumps(kwargs["model_inputs"])) == [{"chunks": [{"encoded_text": {"tokens": [7, 8]}}]}]
    session.stop()


def test_numpy_scalars_in_bare_lists_become_json_numbers(np: Any) -> None:
    """A list built with `list(array)` holds numpy scalars, which `json` cannot encode."""
    sample = _sample(
        {"target_tokens": list(np.array([1, 2], dtype=np.int64))},
        tokens=list(np.array([101, 102], dtype=np.int64)),
    )
    gradient = Gradient(data=list(np.array([0.5], dtype=np.float32)), dtype="D_TYPE_FLOAT32")

    coerced = coerce_sample(sample)

    json.dumps(  # Must be encodable; a numpy scalar left in place raises TypeError here.
        {
            "loss_fn_inputs": coerced["loss_fn_inputs"],
            "model_input": coerced["model_input"],
            "gradient": coerce_gradient(gradient),
        }
    )
    assert coerced["loss_fn_inputs"] == {"target_tokens": {"data": [1, 2], "dtype": "int64"}}
    assert coerced["model_input"]["chunks"][0]["encoded_text"]["tokens"] == [101, 102]  # type: ignore[index]


def test_gradient_without_array_data_is_untouched() -> None:
    gradient = Gradient(data=b"packed", dtype="D_TYPE_FLOAT32")  # type: ignore[typeddict-item]

    assert coerce_gradient(gradient) is gradient


def test_tensor_mapping_keeps_its_other_keys(np: Any) -> None:
    tensor = TensorData(data=np.array([1, 2], dtype=np.int64), dtype="int64", shape=[2])

    coerced = coerce_sample(_sample({"target_tokens": tensor}))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [1, 2], "dtype": "int64", "shape": [2]}


def test_complex_array_under_a_declared_dtype_is_rejected(np: Any) -> None:
    tensor = TensorData(data=np.array([1 + 2j], dtype=np.complex128), dtype="float32")

    with pytest.raises(ValueError, match="unsupported dtype"):
        coerce_sample(_sample({"target_tokens": tensor}, tokens=(1,)))


def test_sparse_tensor_is_rejected(np: Any) -> None:
    tensor = FakeTensor(np.array([1, 2], dtype=np.int64), is_sparse=True)

    with pytest.raises(ValueError, match="sparse tensor"):
        coerce_sample(_sample({"target_tokens": tensor}))


def test_errors_name_the_offending_sample(np: Any) -> None:
    with pytest.raises(ValueError, match=r"samples\[1\]\.loss_fn_inputs\['target_tokens'\]"):
        coerce_sample(_sample({"target_tokens": np.zeros((2, 2), dtype=np.int64)}), "samples[1]")


def test_complex_bare_array_is_rejected(np: Any) -> None:
    with pytest.raises(ValueError, match="unsupported dtype"):
        coerce_sample(_sample({"target_tokens": np.array([1 + 2j], dtype=np.complex128)}, tokens=(1,)))


def test_wide_float_tensor_keeps_its_precision(np: Any) -> None:
    """Only dtypes numpy cannot hold widen; a float64 tensor must not round-trip through float32."""
    tensor = FakeTensor(np.array([0.1, 0.2], dtype=np.float64), dtype_name="torch.float64")

    coerced = coerce_sample(_sample({"advantages": tensor}))

    assert coerced["loss_fn_inputs"]["advantages"] == {"data": [0.1, 0.2], "dtype": "float32"}


def test_float_token_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="must hold integers"):
        coerce_model_input(_model_input([1.5, 2.0]))


def test_declared_int64_over_a_float_list_is_rejected() -> None:
    """The array spelling raises; the list spelling must not ship mislabeled data instead."""
    tensor = TensorData(data=[1.5, 2.5], dtype="int64")

    with pytest.raises(ValueError, match="declares dtype 'int64'"):
        coerce_sample(_sample({"target_tokens": tensor}))


def test_uint64_values_outside_signed_int64_are_rejected(np: Any) -> None:
    with pytest.raises(ValueError, match="outside signed int64"):
        coerce_sample(_sample({"target_tokens": np.array([2**63], dtype=np.uint64)}, tokens=(1,)))


def test_list_values_outside_signed_int64_are_rejected() -> None:
    with pytest.raises(ValueError, match="outside signed int64"):
        coerce_sample(_sample({"target_tokens": [2**63]}, tokens=(1,)))


def test_uint64_token_values_outside_signed_int64_are_rejected(np: Any) -> None:
    with pytest.raises(ValueError, match="outside signed int64"):
        coerce_model_input(_model_input(np.array([2**63], dtype=np.uint64)))


def test_float64_values_outside_float32_are_rejected(np: Any) -> None:
    with pytest.raises(ValueError, match="outside float32"):
        coerce_sample(_sample({"advantages": np.array([6.805646932770577e38], dtype=np.float64)}, tokens=(1,)))


def test_list_values_outside_float32_are_rejected() -> None:
    with pytest.raises(ValueError, match="outside float32"):
        coerce_sample(_sample({"advantages": [6.805646932770577e38]}, tokens=(1,)))


def test_integer_list_outside_float32_is_rejected() -> None:
    with pytest.raises(ValueError, match="outside float32"):
        coerce_sample(_sample({"advantages": [10**100]}, tokens=(1,)))


def test_string_tokens_are_preserved() -> None:
    coerced = coerce_model_input(_model_input(["101", "102"]))

    chunks = list(coerced["chunks"])
    assert chunks[0]["encoded_text"]["tokens"] == ["101", "102"]


def test_torch_tensor_serializes_without_numpy() -> None:
    tensor = FakeTensor([7, 8], numpy_available=False)

    coerced = coerce_sample(_sample({"target_tokens": tensor}))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [7, 8], "dtype": "int64"}


def test_torch_bool_tensor_serializes_without_numpy() -> None:
    tensor = FakeTensor([True, False], dtype_name="torch.bool", numpy_available=False)

    coerced = coerce_sample(_sample({"mask": tensor}))

    assert coerced["loss_fn_inputs"]["mask"] == {"data": [1, 0], "dtype": "int64"}


def test_longdouble_array_narrows_to_native_floats(np: Any) -> None:
    """longdouble is the one float dtype whose tolist() yields numpy scalars, not floats."""
    coerced = coerce_sample(_sample({"advantages": np.array([0.1, 0.2], dtype=np.longdouble)}))

    data = coerced["loss_fn_inputs"]["advantages"]["data"]
    assert json.dumps(data) == "[0.1, 0.2]"
