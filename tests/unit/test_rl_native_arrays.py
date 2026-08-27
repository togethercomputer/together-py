"""Torch/numpy coercion on the native RL clients.

numpy is installed by the ``tinker`` extra, so the numpy cases run on the ``test-tinker``
CI job and skip elsewhere. torch is not installed anywhere in CI — nothing this package
ships depends on it — so the torch branch is covered by ``FakeTensor``, a stub that
enforces the parts of torch's contract the coercion relies on: ``.numpy()`` refuses a
tensor that still carries an autograd graph, lives off the host, or holds ``bfloat16``.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast
from dataclasses import replace, dataclass

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
def numpy() -> Any:
    return pytest.importorskip("numpy")


@dataclass(frozen=True)
class FakeTensor:
    """A torch-shaped stand-in that fails the way a real tensor would."""

    array: Any
    is_floating_point: bool = False
    requires_grad: bool = False
    on_device: bool = False
    bfloat16: bool = False

    @property
    def dtype(self) -> Any:
        return SimpleNamespace(is_floating_point=self.is_floating_point)

    def detach(self) -> FakeTensor:
        return replace(self, requires_grad=False)

    def cpu(self) -> FakeTensor:
        return replace(self, on_device=False)

    def float(self) -> FakeTensor:
        return replace(self, array=self.array.astype("float32"), bfloat16=False)

    def tolist(self) -> list[Any]:  # only ever reached through numpy(); marks this as an array
        return cast("list[Any]", self.array.tolist())

    def numpy(self) -> Any:
        if self.requires_grad:
            raise RuntimeError("Can't call numpy() on Tensor that requires grad")
        if self.on_device:
            raise TypeError("can't convert a device tensor to numpy")
        if self.bfloat16:
            raise TypeError("Got unsupported ScalarType BFloat16")
        return self.array


def _model_input(tokens: Any) -> ModelInput:
    return ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=tokens))])


def _sample(loss_fn_inputs: Any, tokens: Any = (1, 2, 3)) -> Sample:
    return Sample(model_input=_model_input(list(tokens)), loss_fn_inputs=loss_fn_inputs)


def _last_kwargs(client: FakeClient) -> dict[str, Any]:
    assert client.beta.rl.operations.last_call is not None
    return client.beta.rl.operations.last_call[2]


def test_numpy_array_value_takes_the_array_dtype(numpy: Any) -> None:
    coerced = coerce_sample(_sample({"target_tokens": numpy.array([1, 2, 3], dtype=numpy.int32)}))

    assert coerced["loss_fn_inputs"] == {"target_tokens": {"data": [1, 2, 3], "dtype": "int64"}}


def test_tensor_is_detached_and_moved_to_the_host(numpy: Any) -> None:
    advantages = FakeTensor(
        numpy.array([0.5, -0.25], dtype=numpy.float64),
        is_floating_point=True,
        requires_grad=True,
        on_device=True,
    )

    coerced = coerce_sample(_sample({"target_tokens": [1, 2], "advantages": advantages}))

    assert coerced["loss_fn_inputs"]["advantages"] == {"data": [0.5, -0.25], "dtype": "float32"}


def test_bfloat16_widens_to_float32(numpy: Any) -> None:
    advantages = FakeTensor(numpy.array([1.0, 2.0], dtype=numpy.float64), is_floating_point=True, bfloat16=True)

    coerced = coerce_sample(_sample({"advantages": advantages}))

    assert coerced["loss_fn_inputs"]["advantages"] == {"data": [1.0, 2.0], "dtype": "float32"}


def test_integer_tensor_is_not_widened(numpy: Any) -> None:
    target_tokens = FakeTensor(numpy.array([7, 8], dtype=numpy.int64))

    coerced = coerce_sample(_sample({"target_tokens": target_tokens}))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [7, 8], "dtype": "int64"}


def test_tensor_data_with_array_data_keeps_its_declared_dtype(numpy: Any) -> None:
    tensor = TensorData(data=numpy.array([1, 2, 3], dtype=numpy.int64), dtype="int64")

    coerced = coerce_sample(_sample({"target_tokens": tensor}))

    assert coerced["loss_fn_inputs"]["target_tokens"] == {"data": [1, 2, 3], "dtype": "int64"}


def test_plain_lists_infer_the_dtype_their_key_pins() -> None:
    # `advantages` is float32 even though every value is an int, matching tinker's key table.
    coerced = coerce_sample(_sample({"target_tokens": [1, 2], "advantages": [0, 1]}))

    assert coerced["loss_fn_inputs"] == {
        "target_tokens": {"data": [1, 2], "dtype": "int64"},
        "advantages": {"data": [0, 1], "dtype": "float32"},
    }


def test_list_under_an_unknown_key_infers_from_its_values() -> None:
    coerced = coerce_sample(_sample({"target_tokens": [1], "future_input": [0.5]}))

    assert coerced["loss_fn_inputs"]["future_input"] == {"data": [0.5], "dtype": "float32"}


def test_nested_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="flat numeric list"):
        coerce_sample(_sample({"target_tokens": [[1, 2], [3, 4]]}))


def test_json_ready_sample_is_returned_unchanged() -> None:
    sample = _sample({"target_tokens": TensorData(data=[1, 2], dtype="int64")})

    assert coerce_sample(sample) is sample


def test_caller_dict_is_not_mutated(numpy: Any) -> None:
    array = numpy.array([1, 2], dtype=numpy.int64)
    inputs: dict[str, Any] = {"target_tokens": array}
    sample = _sample(inputs)

    coerce_sample(sample)

    assert inputs["target_tokens"] is array


def test_multidimensional_array_is_rejected(numpy: Any) -> None:
    sample = _sample({"target_tokens": numpy.zeros((2, 2), dtype=numpy.int64)})

    with pytest.raises(ValueError, match="2-dimensional"):
        coerce_sample(sample)


def test_unsupported_value_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be a TensorData mapping"):
        coerce_sample(_sample({"target_tokens": object()}))


def test_float_token_array_is_rejected(numpy: Any) -> None:
    with pytest.raises(ValueError, match="must be an integer array"):
        coerce_model_input(_model_input(numpy.array([1.0, 2.0])))


def test_prompt_tokens_become_integers(numpy: Any) -> None:
    coerced = coerce_model_input(_model_input(FakeTensor(numpy.array([101, 102], dtype=numpy.int64))))

    assert coerced["chunks"][0]["encoded_text"]["tokens"] == [101, 102]  # type: ignore[index]


def test_gradient_data_keeps_its_proto_dtype(numpy: Any) -> None:
    gradient = Gradient(data=numpy.array([0.5, -0.5], dtype=numpy.float32), dtype="D_TYPE_FLOAT32")

    assert coerce_gradient(gradient) == {"data": [0.5, -0.5], "dtype": "D_TYPE_FLOAT32"}


def test_forward_backward_submits_serializable_arrays(monkeypatch: pytest.MonkeyPatch, numpy: Any) -> None:
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.trainer.forward_backward(
        samples=[
            Sample(
                model_input=_model_input(numpy.array([1, 2], dtype=numpy.int64)),
                loss_fn_inputs={
                    "target_tokens": numpy.array([1, 2], dtype=numpy.int64),
                    "logprobs": numpy.array([-0.5, -0.25], dtype=numpy.float32),
                    "advantages": numpy.array([1.0, 1.0], dtype=numpy.float32),
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


def test_integer_advantages_array_still_fails_dtype_validation(monkeypatch: pytest.MonkeyPatch, numpy: Any) -> None:
    patch_wait(monkeypatch, ForwardBackwardResult(loss=1.0, metrics={}))
    session = SessionClient("sess", _client=cast(Any, FakeClient()))

    with pytest.raises(ValueError, match=r"advantages'\]\.dtype"):
        session.trainer.forward_backward(
            samples=[
                _sample(
                    {
                        "target_tokens": numpy.array([1, 2], dtype=numpy.int64),
                        "logprobs": numpy.array([-0.5, -0.25], dtype=numpy.float32),
                        "advantages": numpy.array([1, 1], dtype=numpy.int64),
                    }
                )
            ],
            loss=LossConfig(type="LOSS_TYPE_GRPO"),
        )
    session.stop()


def test_custom_forward_backward_serializes_gradient_arrays(monkeypatch: pytest.MonkeyPatch, numpy: Any) -> None:
    patch_wait(monkeypatch, SimpleNamespace(logprobs=[]))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.trainer.custom_forward_backward(
        samples=[_sample({"target_tokens": numpy.array([1, 2], dtype=numpy.int64)})],
        gradients=[Gradient(data=numpy.array([0.5, -0.5], dtype=numpy.float32))],
    )

    kwargs = _last_kwargs(client)
    assert json.loads(json.dumps(kwargs["gradients"])) == [{"data": [0.5, -0.5]}]
    session.stop()


def test_sample_batch_serializes_array_prompts(monkeypatch: pytest.MonkeyPatch, numpy: Any) -> None:
    patch_wait(monkeypatch, SimpleNamespace(results=[SampleResult(policy_segments=[], sequences=[])]))
    client = FakeClient()
    session = SessionClient("sess", _client=cast(Any, client))

    session.generator.sample_batch(prompts=[_model_input(numpy.array([7, 8], dtype=numpy.int32))])

    kwargs = _last_kwargs(client)
    assert json.loads(json.dumps(kwargs["model_inputs"])) == [{"chunks": [{"encoded_text": {"tokens": [7, 8]}}]}]
    session.stop()
