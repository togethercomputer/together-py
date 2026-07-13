from __future__ import annotations

import os
import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from together import AsyncTogether
from together.lib.beta.rl import (
    Loss,
    Prompt,
    Sample,
    Trainer,
    MuonOptimizerParams,
    AdamwOptimizerParams,
    PromptChunk,
    LossGrpoParams,
    SamplingParams,
    SampleLossInputs,
    SampleModelInput,
    SampleModelInputChunk,
    PromptChunkEncodedText,
    SampleLossInputsLossMask,
    SampleLossInputsGrpoInputs,
    SampleLossInputsTargetTokens,
    SampleModelInputChunkEncodedText,
    SampleLossInputsGrpoInputsAdvantages,
    SampleLossInputsGrpoInputsGeneratorLogprobs,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


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
                    "output": {"rollouts": []},
                },
            )
        )

        trainer = Trainer("sess", _client=async_client)
        prompt = Prompt(chunks=[PromptChunk(encoded_text=PromptChunkEncodedText(tokens=[101, 102]))])
        sampling = SamplingParams(
            max_tokens=16,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stop=["\n"],
            seed="123",
        )

        await trainer.sample_async(prompts=[prompt], num_samples=2, sampling_params=sampling)

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "prompts": [prompt],
            "num_samples": 2,
            "sampling_params": sampling,
        }

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_forward_backward_request_body(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
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

        trainer = Trainer("sess", _client=async_client)
        samples = [
            Sample(
                model_input=SampleModelInput(
                    chunks=[
                        SampleModelInputChunk(
                            encoded_text=SampleModelInputChunkEncodedText(
                                tokens=[1, 2, 3],
                            ),
                        )
                    ]
                ),
                loss_inputs=SampleLossInputs(
                    loss_mask=SampleLossInputsLossMask(
                        data=[0, 1, 1],
                        dtype="D_TYPE_INT64",
                    ),
                    target_tokens=SampleLossInputsTargetTokens(
                        data=[2, 3, 0],
                        dtype="D_TYPE_INT64",
                    ),
                    grpo_inputs=SampleLossInputsGrpoInputs(
                        advantages=SampleLossInputsGrpoInputsAdvantages(
                            data=[1.0, 1.0, 1.0],
                            dtype="D_TYPE_FLOAT32",
                        ),
                        generator_logprobs=SampleLossInputsGrpoInputsGeneratorLogprobs(
                            data=[-0.1, -0.2, -0.3],
                            dtype="D_TYPE_FLOAT32",
                        ),
                    ),
                ),
            )
        ]
        loss = Loss(
            type="LOSS_TYPE_GRPO",
            grpo_params=LossGrpoParams(
                agg_type="GRPO_LOSS_AGGREGATION_TYPE_TOKEN_MEAN",
                beta=0.1,
            ),
        )

        await trainer.forward_backward_async(samples=samples, loss=loss)

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "loss": loss,
            "samples": samples,
        }

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

        trainer = Trainer("sess", _client=async_client)

        adamw = AdamwOptimizerParams(
            beta1=0.9,
            beta2=0.95,
            eps=1e-8,
            learning_rate=1e-4,
            weight_decay=0.1,
        )
        await trainer.optim_step_async(adamw_params=adamw)

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "weight_sync_type": "WEIGHT_SYNC_TYPE_UNSPECIFIED",
            "adamw_params": adamw,
        }

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_optim_step_muon_in_wire_body(
        self, async_client: AsyncTogether, respx_mock: MockRouter
    ) -> None:
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

        trainer = Trainer("sess", _client=async_client)
        muon = MuonOptimizerParams(learning_rate=0.02, momentum=0.95, newton_schulz_steps=5, weight_decay=0.0)
        await trainer.optim_step_async(
            muon_params=muon,
        )

        call = cast(Any, respx_mock.calls[0])
        request = cast(httpx.Request, call.request)
        body = json.loads(request.content)
        assert body == {
            "weight_sync_type": "WEIGHT_SYNC_TYPE_UNSPECIFIED",
            "muon_params": muon,
        }

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

        trainer = Trainer("sess", _client=async_client)
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

        trainer = Trainer("sess", _client=async_client)
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

        from together.lib.beta.rl import trainer as rl_trainer_module

        monkeypatch.setattr(rl_trainer_module, "AsyncTogether", fake_together)

        await Trainer.create_async(
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
        trainer = Trainer("sess", _client=cast(Any, fake_client))

        paths = await trainer.download_checkpoint_async("ckpt-1", output_dir=tmp_path)

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
        trainer = Trainer("sess", _client=async_client)

        paths = await trainer.download_checkpoint_async("ckpt-1", output_dir=tmp_path)

        assert [path.name for path in paths] == ["a.bin", "b.bin"]
        assert (tmp_path / "a.bin").read_bytes() == b"a"
        assert (tmp_path / "b.bin").read_bytes() == b"bb"
