# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    FineTune,
    FineTuningListResponse,
    FineTuningCancelResponse,
    FineTuningCreateResponse,
    FineTuningDeleteResponse,
    FineTuningListEventsResponse,
    FineTuningListCheckpointsResponse,
)
from together._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFineTuning:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.create(
            model="model",
            training_file="training_file",
        )
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.create(
            model="model",
            training_file="training_file",
            batch_size=0,
            from_checkpoint="from_checkpoint",
            from_hf_model="from_hf_model",
            hf_api_token="hf_api_token",
            hf_model_revision="hf_model_revision",
            hf_output_repo_name="hf_output_repo_name",
            learning_rate=0,
            lr_scheduler={
                "lr_scheduler_type": "linear",
                "lr_scheduler_args": {"min_lr_ratio": 0},
            },
            max_grad_norm=0,
            n_checkpoints=0,
            n_epochs=0,
            n_evals=0,
            suffix="suffix",
            train_on_inputs=True,
            training_method={
                "method": "sft",
                "train_on_inputs": True,
            },
            training_type={"type": "Full"},
            validation_file="validation_file",
            wandb_api_key="wandb_api_key",
            wandb_base_url="wandb_base_url",
            wandb_name="wandb_name",
            wandb_project_name="wandb_project_name",
            warmup_ratio=0,
            weight_decay=0,
        )
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.create(
            model="model",
            training_file="training_file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.create(
            model="model",
            training_file="training_file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.retrieve(
            "id",
        )
        assert_matches_type(FineTune, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTune, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTune, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tuning.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.list()
        assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.delete(
            id="id",
            force=True,
        )
        assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.delete(
            id="id",
            force=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.delete(
            id="id",
            force=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tuning.with_raw_response.delete(
                id="",
                force=True,
            )

    @parametrize
    def test_method_cancel(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.cancel(
            "id",
        )
        assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.cancel(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.cancel(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tuning.with_raw_response.cancel(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        fine_tuning = client.fine_tuning.download(
            ft_id="ft_id",
        )
        assert fine_tuning.is_closed
        assert fine_tuning.json() == {"foo": "bar"}
        assert cast(Any, fine_tuning.is_closed) is True
        assert isinstance(fine_tuning, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_with_all_params(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        fine_tuning = client.fine_tuning.download(
            ft_id="ft_id",
            checkpoint="merged",
            checkpoint_step=0,
        )
        assert fine_tuning.is_closed
        assert fine_tuning.json() == {"foo": "bar"}
        assert cast(Any, fine_tuning.is_closed) is True
        assert isinstance(fine_tuning, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        fine_tuning = client.fine_tuning.with_raw_response.download(
            ft_id="ft_id",
        )

        assert fine_tuning.is_closed is True
        assert fine_tuning.http_request.headers.get("X-Stainless-Lang") == "python"
        assert fine_tuning.json() == {"foo": "bar"}
        assert isinstance(fine_tuning, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.fine_tuning.with_streaming_response.download(
            ft_id="ft_id",
        ) as fine_tuning:
            assert not fine_tuning.is_closed
            assert fine_tuning.http_request.headers.get("X-Stainless-Lang") == "python"

            assert fine_tuning.json() == {"foo": "bar"}
            assert cast(Any, fine_tuning.is_closed) is True
            assert isinstance(fine_tuning, StreamedBinaryAPIResponse)

        assert cast(Any, fine_tuning.is_closed) is True

    @parametrize
    def test_method_list_checkpoints(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.list_checkpoints(
            "id",
        )
        assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_list_checkpoints(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.list_checkpoints(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_list_checkpoints(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.list_checkpoints(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_checkpoints(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tuning.with_raw_response.list_checkpoints(
                "",
            )

    @parametrize
    def test_method_list_events(self, client: Together) -> None:
        fine_tuning = client.fine_tuning.list_events(
            "id",
        )
        assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

    @parametrize
    def test_raw_response_list_events(self, client: Together) -> None:
        response = client.fine_tuning.with_raw_response.list_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = response.parse()
        assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

    @parametrize
    def test_streaming_response_list_events(self, client: Together) -> None:
        with client.fine_tuning.with_streaming_response.list_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = response.parse()
            assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_events(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fine_tuning.with_raw_response.list_events(
                "",
            )


class TestAsyncFineTuning:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.create(
            model="model",
            training_file="training_file",
        )
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.create(
            model="model",
            training_file="training_file",
            batch_size=0,
            from_checkpoint="from_checkpoint",
            from_hf_model="from_hf_model",
            hf_api_token="hf_api_token",
            hf_model_revision="hf_model_revision",
            hf_output_repo_name="hf_output_repo_name",
            learning_rate=0,
            lr_scheduler={
                "lr_scheduler_type": "linear",
                "lr_scheduler_args": {"min_lr_ratio": 0},
            },
            max_grad_norm=0,
            n_checkpoints=0,
            n_epochs=0,
            n_evals=0,
            suffix="suffix",
            train_on_inputs=True,
            training_method={
                "method": "sft",
                "train_on_inputs": True,
            },
            training_type={"type": "Full"},
            validation_file="validation_file",
            wandb_api_key="wandb_api_key",
            wandb_base_url="wandb_base_url",
            wandb_name="wandb_name",
            wandb_project_name="wandb_project_name",
            warmup_ratio=0,
            weight_decay=0,
        )
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.create(
            model="model",
            training_file="training_file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.create(
            model="model",
            training_file="training_file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningCreateResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.retrieve(
            "id",
        )
        assert_matches_type(FineTune, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTune, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTune, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tuning.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.list()
        assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningListResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.delete(
            id="id",
            force=True,
        )
        assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.delete(
            id="id",
            force=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.delete(
            id="id",
            force=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningDeleteResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tuning.with_raw_response.delete(
                id="",
                force=True,
            )

    @parametrize
    async def test_method_cancel(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.cancel(
            "id",
        )
        assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.cancel(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.cancel(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningCancelResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tuning.with_raw_response.cancel(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        fine_tuning = await async_client.fine_tuning.download(
            ft_id="ft_id",
        )
        assert fine_tuning.is_closed
        assert await fine_tuning.json() == {"foo": "bar"}
        assert cast(Any, fine_tuning.is_closed) is True
        assert isinstance(fine_tuning, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_with_all_params(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        fine_tuning = await async_client.fine_tuning.download(
            ft_id="ft_id",
            checkpoint="merged",
            checkpoint_step=0,
        )
        assert fine_tuning.is_closed
        assert await fine_tuning.json() == {"foo": "bar"}
        assert cast(Any, fine_tuning.is_closed) is True
        assert isinstance(fine_tuning, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        fine_tuning = await async_client.fine_tuning.with_raw_response.download(
            ft_id="ft_id",
        )

        assert fine_tuning.is_closed is True
        assert fine_tuning.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await fine_tuning.json() == {"foo": "bar"}
        assert isinstance(fine_tuning, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.get("/finetune/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.fine_tuning.with_streaming_response.download(
            ft_id="ft_id",
        ) as fine_tuning:
            assert not fine_tuning.is_closed
            assert fine_tuning.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await fine_tuning.json() == {"foo": "bar"}
            assert cast(Any, fine_tuning.is_closed) is True
            assert isinstance(fine_tuning, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, fine_tuning.is_closed) is True

    @parametrize
    async def test_method_list_checkpoints(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.list_checkpoints(
            "id",
        )
        assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_list_checkpoints(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.list_checkpoints(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_list_checkpoints(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.list_checkpoints(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningListCheckpointsResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_checkpoints(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tuning.with_raw_response.list_checkpoints(
                "",
            )

    @parametrize
    async def test_method_list_events(self, async_client: AsyncTogether) -> None:
        fine_tuning = await async_client.fine_tuning.list_events(
            "id",
        )
        assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncTogether) -> None:
        response = await async_client.fine_tuning.with_raw_response.list_events(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tuning = await response.parse()
        assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncTogether) -> None:
        async with async_client.fine_tuning.with_streaming_response.list_events(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tuning = await response.parse()
            assert_matches_type(FineTuningListEventsResponse, fine_tuning, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fine_tuning.with_raw_response.list_events(
                "",
            )
