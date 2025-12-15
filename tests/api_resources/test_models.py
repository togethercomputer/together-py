# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import ModelListResponse, ModelUploadResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Together) -> None:
        model = client.models.list()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        model = client.models.list(
            dedicated=True,
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_upload(self, client: Together) -> None:
        model = client.models.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        )
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    def test_method_upload_with_all_params(self, client: Together) -> None:
        model = client.models.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
            base_model="Qwen/Qwen2.5-72B-Instruct",
            description="Finetuned Qwen2.5-72B-Instruct by Unsloth",
            hf_token="hf_examplehuggingfacetoken",
            lora_model="my_username/Qwen2.5-72B-Instruct-lora",
            model_type="model",
        )
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    def test_raw_response_upload(self, client: Together) -> None:
        response = client.models.with_raw_response.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = response.parse()
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    def test_streaming_response_upload(self, client: Together) -> None:
        with client.models.with_streaming_response.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = response.parse()
            assert_matches_type(ModelUploadResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        model = await async_client.models.list()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        model = await async_client.models.list(
            dedicated=True,
        )
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.models.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelListResponse, model, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.models.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelListResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_upload(self, async_client: AsyncTogether) -> None:
        model = await async_client.models.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        )
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncTogether) -> None:
        model = await async_client.models.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
            base_model="Qwen/Qwen2.5-72B-Instruct",
            description="Finetuned Qwen2.5-72B-Instruct by Unsloth",
            hf_token="hf_examplehuggingfacetoken",
            lora_model="my_username/Qwen2.5-72B-Instruct-lora",
            model_type="model",
        )
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncTogether) -> None:
        response = await async_client.models.with_raw_response.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model = await response.parse()
        assert_matches_type(ModelUploadResponse, model, path=["response"])

    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncTogether) -> None:
        async with async_client.models.with_streaming_response.upload(
            model_name="Qwen2.5-72B-Instruct",
            model_source="unsloth/Qwen2.5-72B-Instruct",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model = await response.parse()
            assert_matches_type(ModelUploadResponse, model, path=["response"])

        assert cast(Any, response.is_closed) is True
