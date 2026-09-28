from __future__ import annotations

import os
import json
import importlib
from types import SimpleNamespace
from typing import Any, cast, get_args, get_origin, get_type_hints
from unittest.mock import AsyncMock, MagicMock
from collections.abc import Callable, Awaitable
from typing_extensions import Required

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from together import Together, AsyncTogether
from together.lib.beta.rl import (
    Sample,
    Trainer,
    AdamParams,
    LossConfig,
    ModelInput,
    MuonParams,
    TensorData,
    SessionClient,
    DppoLossParams,
    GrpoLossParams,
    SamplingParams,
    ModelInputChunk,
    EncodedTextChunk,
    _losses as rl_losses,
    download_checkpoint,
    download_checkpoint_async,
)
from together.types.beta.rl import (
    loss_config_param,
    tensor_data_param,
    operation_forward_backward_params,
    operation_custom_forward_backward_params,
)
from together.lib.beta.rl._payloads import _VALIDATION_OMITTED_KEYS

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

LEGACY_RL_LOSS_INPUT_NAMES = frozenset(
    {
        "LossInputs",
        "LossTargetTokens",
        "Weights",
        "LossAdvantages",
        "LossLogprobs",
        "GrpoLossInputs",
        "PpoLossInputs",
        "CispoLossInputs",
        "DroLossInputs",
        "ImportanceSamplingLossInputs",
    }
)


ForwardBackwardCall = Callable[[Trainer, list[Sample], LossConfig], Awaitable[object]]

# Each case pairs a trainer call with the flag keys its request body must carry: an ordinary
# forward_backward sends neither flag, while an explicit False must reach the wire as false.
FORWARD_BACKWARD_FLAG_CASES: list[tuple[ForwardBackwardCall, dict[str, bool]]] = [
    (
        lambda trainer, samples, loss: trainer.forward_async(samples=samples, loss=loss),
        {"forward_only": True, "return_loss_fn_outputs": True},
    ),
    (lambda trainer, samples, loss: trainer.forward_backward_async(samples=samples, loss=loss), {}),
    (
        lambda trainer, samples, loss: trainer.forward_backward_async(
            samples=samples, loss=loss, return_loss_fn_outputs=True
        ),
        {"return_loss_fn_outputs": True},
    ),
    (
        lambda trainer, samples, loss: trainer.forward_backward_async(
            samples=samples, loss=loss, return_loss_fn_outputs=False
        ),
        {"return_loss_fn_outputs": False},
    ),
]


class TestRLRequestBody:
    parametrize = pytest.mark.parametrize("async_client", [False], indirect=True, ids=["loose"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_sample_request_body(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/sample").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/sample/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"results": []},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        generator = trainer.generator
        model_input = ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[101, 102]))])
        sampling = SamplingParams(
            max_tokens=16,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stop=["\n"],
            seed="123",
        )

        result = await generator.sample_batch_async(
            prompts=[model_input],
            num_samples=2,
            sampling_params=sampling,
        )

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "model_inputs": [model_input],
            "num_samples": 2,
            "sampling_params": sampling,
        }
        assert result == []

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        "loss",
        [
            LossConfig(
                type="LOSS_TYPE_GRPO",
                grpo_params=GrpoLossParams(agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN", beta=0.1),
            ),
            LossConfig(type="LOSS_TYPE_DPPO"),
            LossConfig(type="LOSS_TYPE_DPPO", dppo_params=DppoLossParams(delta_low=0.1, delta_high=0.2)),
        ],
    )
    async def test_forward_backward_request_body(
        self, async_client: AsyncTogether, respx_mock: MockRouter, loss: LossConfig
    ) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/forward-backward").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/forward-backward/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"loss": 1.0, "metrics": {}},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        samples = [
            Sample(
                model_input=ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3, 4]))]),
                # full = [1, 2, 3, 4, 5], prompt = [1, 2, 3] (P=3), response = [4, 5]: every
                # array below is indexed by target position, so each carries a zero prefix of
                # length P-1 == 2.
                loss_fn_inputs={
                    "weights": TensorData(
                        data=[0.0, 0.0, 1.0, 1.0],
                        dtype="float32",
                    ),
                    "target_tokens": TensorData(
                        data=[2, 3, 4, 5],  # full[1:]
                        dtype="int64",
                    ),
                    "advantages": TensorData(
                        data=[0.0, 0.0, 1.0, 1.0],
                        dtype="float32",
                    ),
                    "logprobs": TensorData(
                        data=[0.0, 0.0, -0.2, -0.3],
                        dtype="float32",
                    ),
                },
            )
        ]
        if loss["type"] == "LOSS_TYPE_GRPO":
            samples[0]["loss_fn_inputs"] = {
                **samples[0]["loss_fn_inputs"],
                "reference_logprobs": TensorData(data=[0.0, 0.0, -0.3, -0.4], dtype="float32"),
            }
        await trainer.trainer.forward_backward_async(samples=samples, loss=loss)

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "loss": loss,
            "samples": samples,
        }

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.parametrize(
        ("call", "expected_flags"),
        FORWARD_BACKWARD_FLAG_CASES,
        ids=["forward", "forward_backward", "forward_backward_outputs_true", "forward_backward_outputs_false"],
    )
    async def test_forward_backward_flags_in_wire_body(
        self,
        async_client: AsyncTogether,
        respx_mock: MockRouter,
        call: ForwardBackwardCall,
        expected_flags: dict[str, bool],
    ) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/forward-backward").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/forward-backward/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"loss": 1.0, "metrics": {}},
                },
            )
        )

        session = SessionClient("sess", _client=async_client)
        samples = [
            Sample(
                model_input=ModelInput(chunks=[ModelInputChunk(encoded_text=EncodedTextChunk(tokens=[1, 2, 3, 4]))]),
                # full = [1, 2, 3, 4, 5], prompt = [1, 2, 3] (P=3); target-indexed, zero prefix P-1 == 2.
                loss_fn_inputs={
                    "weights": TensorData(data=[0.0, 0.0, 1.0, 1.0], dtype="float32"),
                    "target_tokens": TensorData(data=[2, 3, 4, 5], dtype="int64"),
                    "advantages": TensorData(data=[0.0, 0.0, 1.0, 1.0], dtype="float32"),
                    "logprobs": TensorData(data=[0.0, 0.0, -0.2, -0.3], dtype="float32"),
                },
            )
        ]
        loss = LossConfig(
            type="LOSS_TYPE_GRPO",
            grpo_params=GrpoLossParams(agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN", beta=0.1),
        )

        samples[0]["loss_fn_inputs"] = {
            **samples[0]["loss_fn_inputs"],
            "reference_logprobs": TensorData(data=[0.0, 0.0, -0.3, -0.4], dtype="float32"),
        }
        await call(session.trainer, samples, loss)

        request = cast(httpx.Request, cast(Any, respx_mock.calls[0]).request)
        body = json.loads(request.content)
        assert body == {"loss": loss, "samples": samples, **expected_flags}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_optim_step_request_body(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/optim-step").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/optim-step/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"step": "1"},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)

        adam = AdamParams(
            beta1=0.9,
            beta2=0.95,
            eps=1e-8,
            grad_clip_norm=1.0,
            learning_rate=1e-4,
            weight_decay=0.1,
        )
        await trainer.trainer.optim_step_async(adam_params=adam)

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "adam_params": adam,
        }

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_optim_step_muon_in_wire_body(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/optim-step").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/optim-step/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"step": "1"},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        muon = MuonParams(
            learning_rate=0.02,
            momentum=0.95,
            newton_schulz_steps=5,
            weight_decay=0.0,
            grad_clip_norm=1.0,
            adam=AdamParams(beta1=0.9, learning_rate=1e-4),
        )
        await trainer.trainer.optim_step_async(
            muon_params=muon,
        )

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "muon_params": muon,
        }

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_weights_sync_request_body(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/weights-sync").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/weights-sync/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"weights_version": 1},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        result = await trainer.trainer.weights_sync_async(
            weight_sync_type="WEIGHT_SYNC_TYPE_SYNCHRONOUS",
        )

        assert int(result.weights_version) == 1
        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {"weight_sync_type": "WEIGHT_SYNC_TYPE_SYNCHRONOUS"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_create_training_checkpoint_post(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/training-checkpoint").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/training-checkpoint/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"checkpoint_id": "ckpt-1"},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        await trainer.create_training_checkpoint_async()

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        assert "/rl/training-sessions/sess/operations/training-checkpoint" in str(request.url)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_create_inference_checkpoint_post(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/rl/training-sessions/sess/operations/inference-checkpoint").mock(
            return_value=httpx.Response(200, json={"id": "op-1"})
        )
        respx_mock.get("/rl/training-sessions/sess/operations/inference-checkpoint/op-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "op-1",
                    "status": "TRAINING_OPERATION_STATUS_COMPLETED",
                    "output": {"model_name": "model-1"},
                },
            )
        )

        trainer = SessionClient("sess", _client=async_client)
        await trainer.create_inference_checkpoint_async()

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        assert "/rl/training-sessions/sess/operations/inference-checkpoint" in str(request.url)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_create_session_request_body_attaches_to_model_resources(
        self,
        async_client: AsyncTogether,
        respx_mock: MockRouter,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        respx_mock.get("/rl/model-resources/res-1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "res-1",
                    "base_model": "Qwen/Qwen3-0.6B",
                    "compute_config": {"num_generator_replicas": 1},
                    "created_at": "2026-01-01T00:00:00Z",
                    "created_by": "user-1",
                    "lora_enabled": True,
                    "optimizer_config": {},
                    "status": "MODEL_RESOURCES_STATUS_READY",
                    "updated_at": "2026-01-01T00:00:00Z",
                },
            )
        )
        respx_mock.post("/rl/training-sessions").mock(
            return_value=httpx.Response(
                200,
                json={"id": "sess-1", "status": "TRAINING_SESSION_STATUS_RUNNING"},
            )
        )
        respx_mock.get("/rl/training-sessions/sess-1").mock(
            return_value=httpx.Response(
                200,
                json={"id": "sess-1", "status": "TRAINING_SESSION_STATUS_RUNNING"},
            )
        )

        def fake_together(**_kw: Any) -> AsyncTogether:
            return async_client

        from together.lib.beta.rl.clients import session as session_client_module

        monkeypatch.setattr(session_client_module, "AsyncTogether", fake_together)

        await SessionClient.create_async(
            model_resources_id="res-1",
            timeout=1.0,
            interval=0.0,
        )

        calls = cast("list[Call]", list(respx_mock.calls))
        create_call = next(call for call in calls if call.request.method == "POST")
        body = json.loads(create_call.request.content)
        assert body["model_resources_id"] == "res-1"

    async def test_download_checkpoint_async_returns_empty_list_for_empty_data(self, tmp_path: Any) -> None:
        fake_client = SimpleNamespace(
            beta=SimpleNamespace(
                rl=SimpleNamespace(
                    checkpoints=SimpleNamespace(
                        download=AsyncMock(return_value=SimpleNamespace(data=[])),
                    )
                )
            )
        )

        paths = await download_checkpoint_async(cast(Any, fake_client), "ckpt-1", output_dir=tmp_path)

        assert paths == []

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_download_checkpoint_async_downloads_files(
        self, async_client: AsyncTogether, respx_mock: MockRouter, tmp_path: Any
    ) -> None:
        respx_mock.get("https://files.test/a.bin").mock(return_value=httpx.Response(200, content=b"a"))
        respx_mock.get("https://files.test/b.bin").mock(return_value=httpx.Response(200, content=b"bb"))

        async_client.beta.rl.checkpoints.download = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(
                data=[
                    SimpleNamespace(url="https://files.test/a.bin", filename="a.bin"),
                    SimpleNamespace(url="https://files.test/b.bin", filename="b.bin"),
                ]
            )
        )
        paths = await download_checkpoint_async(async_client, "ckpt-1", output_dir=tmp_path)

        assert [path.name for path in paths] == ["a.bin", "b.bin"]
        assert (tmp_path / "a.bin").read_bytes() == b"a"
        assert (tmp_path / "b.bin").read_bytes() == b"bb"
        calls = cast("list[Call]", list(respx_mock.calls))
        assert all("authorization" not in call.request.headers for call in calls)


@pytest.mark.respx(base_url=base_url)
def test_download_checkpoint_downloads_files(client: Together, respx_mock: MockRouter, tmp_path: Any) -> None:
    respx_mock.get("https://files.test/a.bin").mock(return_value=httpx.Response(200, content=b"a"))
    respx_mock.get("https://files.test/b.bin").mock(return_value=httpx.Response(200, content=b"bb"))

    client.beta.rl.checkpoints.download = MagicMock(  # type: ignore[method-assign]
        return_value=SimpleNamespace(
            data=[
                SimpleNamespace(url="https://files.test/a.bin", filename="a.bin"),
                SimpleNamespace(url="https://files.test/b.bin", filename="b.bin"),
            ]
        )
    )

    paths = download_checkpoint(client, "ckpt-1", output_dir=tmp_path)

    assert [path.name for path in paths] == ["a.bin", "b.bin"]
    assert (tmp_path / "a.bin").read_bytes() == b"a"
    assert (tmp_path / "b.bin").read_bytes() == b"bb"
    calls = cast("list[Call]", list(respx_mock.calls))
    assert all("authorization" not in call.request.headers for call in calls)


@pytest.mark.parametrize("filename", ["../escape.bin", "nested/escape.bin", "/escape.bin"])
def test_download_checkpoint_rejects_unsafe_filename(filename: str, tmp_path: Any) -> None:
    client = MagicMock()
    client.beta.rl.checkpoints.download.return_value = SimpleNamespace(
        data=[SimpleNamespace(url="https://files.test/escape.bin", filename=filename)]
    )
    client.get.side_effect = AssertionError("unsafe filename must be rejected before download")

    with pytest.raises(ValueError, match="Unsafe checkpoint filename"):
        download_checkpoint(cast(Together, client), "ckpt-1", output_dir=tmp_path)

    client.get.assert_not_called()


def test_public_rl_names_have_no_param_suffix() -> None:
    module = importlib.import_module("together.lib.beta.rl")
    param_names = [name for name in module.__all__ if name.endswith("Param")]
    assert param_names == []


def test_public_rl_names_are_importable() -> None:
    module = importlib.import_module("together.lib.beta.rl")
    assert [name for name in module.__all__ if not hasattr(module, name)] == []


def test_public_rl_legacy_loss_inputs_are_not_exported() -> None:
    module = importlib.import_module("together.lib.beta.rl")
    assert LEGACY_RL_LOSS_INPUT_NAMES.isdisjoint(module.__all__)
    assert all(not hasattr(module, name) for name in LEGACY_RL_LOSS_INPUT_NAMES)


def _generated_sample_shapes() -> list[Any]:
    """Every generated sample TypedDict the handwritten Sample stands in for."""
    return [
        operation_forward_backward_params.Sample,
        operation_custom_forward_backward_params.Sample,
    ]


def test_handwritten_sample_matches_generated_shape() -> None:
    """Assert the handwritten Sample still matches every generated sample shape.

    Nothing else syncs it with codegen, so a field added to any generated sample shape
    must fail here rather than silently narrowing the public surface.
    """
    shapes = _generated_sample_shapes()
    assert len(shapes) > 1

    for shape in shapes:
        generated_keys = set(get_type_hints(shape))
        assert set(Sample.__annotations__) == generated_keys, shape.__name__

    required_keys, _ = rl_losses._split_required(get_type_hints(Sample, include_extras=True))
    assert required_keys == {"model_input", "loss_fn_inputs"}


def test_handwritten_loss_config_matches_generated_shape() -> None:
    """The stable facade must expose every field in the generated loss config."""
    assert set(LossConfig.__annotations__) == set(get_type_hints(loss_config_param.LossConfig))


def test_native_loss_specs_cover_generated_loss_types() -> None:
    generated_loss_types = set(get_args(rl_losses.LossType)) - {"LOSS_TYPE_UNSPECIFIED"}
    assert set(rl_losses.LOSS_SPECS) == generated_loss_types


def test_loss_specs_only_use_known_tensor_inputs() -> None:
    for spec in (*rl_losses.LOSS_SPECS.values(), rl_losses.CUSTOM_FORWARD_BACKWARD_INPUTS):
        assert spec.required_inputs | spec.optional_inputs <= rl_losses.INPUT_DTYPES.keys()


def test_validation_omitted_keys_stay_optional() -> None:
    """Assert every key the validation body drops is optional where it lives.

    `_shrink_for_validation` drops these keys, which is only valid while codegen leaves
    them optional. If a future spec marked one Required, every large-payload operation
    would start failing server-side validation with nothing failing locally.
    """
    # The pinned set keeps a new _VALIDATION_OMITTED_KEYS entry from skipping this test.
    assert _VALIDATION_OMITTED_KEYS == {"shape", "sparse_crow_indices", "sparse_col_indices"}

    tensor_hints = get_type_hints(tensor_data_param.TensorDataParam, include_extras=True)
    for key in ("shape", "sparse_crow_indices", "sparse_col_indices"):
        assert get_origin(tensor_hints[key]) is not Required, key
