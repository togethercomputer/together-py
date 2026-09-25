# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import (
    ModelResources,
    ModelResourcesListResponse,
    ModelResourcesEstimateCostResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestModelResources:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.create(
            base_model="Qwen/Qwen3.5-4B",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.create(
            base_model="Qwen/Qwen3.5-4B",
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
            },
            lora_enabled=True,
            optimizer_config={
                "adam": {},
                "muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_ORIGINAL"},
            },
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.beta.rl.model_resources.with_raw_response.create(
            base_model="Qwen/Qwen3.5-4B",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.beta.rl.model_resources.with_streaming_response.create(
            base_model="Qwen/Qwen3.5-4B",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.retrieve(
            "model_resources_id",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.rl.model_resources.with_raw_response.retrieve(
            "model_resources_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.rl.model_resources.with_streaming_response.retrieve(
            "model_resources_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_resources_id` but received ''"):
            client.beta.rl.model_resources.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.list()
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.list(
            after="after",
            created_by="created_by",
            limit=0,
            status=["MODEL_RESOURCES_STATUS_PENDING"],
        )
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.rl.model_resources.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = response.parse()
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.rl.model_resources.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = response.parse()
            assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_estimate_cost(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        )
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    def test_method_estimate_cost_with_all_params(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
            },
            lora_enabled=True,
            optimizer_config={
                "adam": {},
                "muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_ORIGINAL"},
            },
        )
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    def test_raw_response_estimate_cost(self, client: Together) -> None:
        response = client.beta.rl.model_resources.with_raw_response.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = response.parse()
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    def test_streaming_response_estimate_cost(self, client: Together) -> None:
        with client.beta.rl.model_resources.with_streaming_response.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = response.parse()
            assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_stop(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.stop(
            model_resources_id="model_resources_id",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_method_stop_with_all_params(self, client: Together) -> None:
        model_resource = client.beta.rl.model_resources.stop(
            model_resources_id="model_resources_id",
            force=True,
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_raw_response_stop(self, client: Together) -> None:
        response = client.beta.rl.model_resources.with_raw_response.stop(
            model_resources_id="model_resources_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    def test_streaming_response_stop(self, client: Together) -> None:
        with client.beta.rl.model_resources.with_streaming_response.stop(
            model_resources_id="model_resources_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_stop(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_resources_id` but received ''"):
            client.beta.rl.model_resources.with_raw_response.stop(
                model_resources_id="",
            )


class TestAsyncModelResources:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.create(
            base_model="Qwen/Qwen3.5-4B",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.create(
            base_model="Qwen/Qwen3.5-4B",
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
            },
            lora_enabled=True,
            optimizer_config={
                "adam": {},
                "muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_ORIGINAL"},
            },
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.model_resources.with_raw_response.create(
            base_model="Qwen/Qwen3.5-4B",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = await response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.model_resources.with_streaming_response.create(
            base_model="Qwen/Qwen3.5-4B",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = await response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.retrieve(
            "model_resources_id",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.model_resources.with_raw_response.retrieve(
            "model_resources_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = await response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.model_resources.with_streaming_response.retrieve(
            "model_resources_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = await response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_resources_id` but received ''"):
            await async_client.beta.rl.model_resources.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.list()
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.list(
            after="after",
            created_by="created_by",
            limit=0,
            status=["MODEL_RESOURCES_STATUS_PENDING"],
        )
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.model_resources.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = await response.parse()
        assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.model_resources.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = await response.parse()
            assert_matches_type(ModelResourcesListResponse, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_estimate_cost(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        )
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    async def test_method_estimate_cost_with_all_params(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
            compute_config={
                "gpu_type": "B200-SXM",
                "num_generator_replicas": 2,
            },
            lora_enabled=True,
            optimizer_config={
                "adam": {},
                "muon": {"scaling_strategy": "MUON_SCALING_STRATEGY_ORIGINAL"},
            },
        )
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    async def test_raw_response_estimate_cost(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.model_resources.with_raw_response.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = await response.parse()
        assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

    @parametrize
    async def test_streaming_response_estimate_cost(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.model_resources.with_streaming_response.estimate_cost(
            base_model="Qwen/Qwen3.5-4B",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = await response.parse()
            assert_matches_type(ModelResourcesEstimateCostResponse, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_stop(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.stop(
            model_resources_id="model_resources_id",
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_method_stop_with_all_params(self, async_client: AsyncTogether) -> None:
        model_resource = await async_client.beta.rl.model_resources.stop(
            model_resources_id="model_resources_id",
            force=True,
        )
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_raw_response_stop(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.model_resources.with_raw_response.stop(
            model_resources_id="model_resources_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        model_resource = await response.parse()
        assert_matches_type(ModelResources, model_resource, path=["response"])

    @parametrize
    async def test_streaming_response_stop(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.model_resources.with_streaming_response.stop(
            model_resources_id="model_resources_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            model_resource = await response.parse()
            assert_matches_type(ModelResources, model_resource, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_stop(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `model_resources_id` but received ''"):
            await async_client.beta.rl.model_resources.with_raw_response.stop(
                model_resources_id="",
            )
