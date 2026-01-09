# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    DedicatedEndpoint,
    EndpointListResponse,
    EndpointListAvzonesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEndpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        endpoint = client.endpoints.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        endpoint = client.endpoints.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
            availability_zone="availability_zone",
            disable_prompt_cache=True,
            disable_speculative_decoding=True,
            display_name="My Llama3 70b endpoint",
            inactive_timeout=60,
            state="STARTED",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        endpoint = client.endpoints.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: Together) -> None:
        endpoint = client.endpoints.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: Together) -> None:
        endpoint = client.endpoints.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            display_name="My Llama3 70b endpoint",
            inactive_timeout=60,
            state="STARTED",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.with_raw_response.update(
                endpoint_id="",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        endpoint = client.endpoints.list()
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        endpoint = client.endpoints.list(
            mine=True,
            type="dedicated",
            usage_type="on-demand",
        )
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(EndpointListResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Together) -> None:
        endpoint = client.endpoints.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert endpoint is None

    @parametrize
    def test_raw_response_delete(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert endpoint is None

    @parametrize
    def test_streaming_response_delete(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert endpoint is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_list_avzones(self, client: Together) -> None:
        endpoint = client.endpoints.list_avzones()
        assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

    @parametrize
    def test_raw_response_list_avzones(self, client: Together) -> None:
        response = client.endpoints.with_raw_response.list_avzones()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = response.parse()
        assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

    @parametrize
    def test_streaming_response_list_avzones(self, client: Together) -> None:
        with client.endpoints.with_streaming_response.list_avzones() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = response.parse()
            assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEndpoints:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
            availability_zone="availability_zone",
            disable_prompt_cache=True,
            disable_speculative_decoding=True,
            display_name="My Llama3 70b endpoint",
            inactive_timeout=60,
            state="STARTED",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.create(
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            hardware="1x_nvidia_a100_80gb_sxm",
            model="meta-llama/Llama-3-8b-chat-hf",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.retrieve(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
            autoscaling={
                "max_replicas": 5,
                "min_replicas": 2,
            },
            display_name="My Llama3 70b endpoint",
            inactive_timeout=60,
            state="STARTED",
        )
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.update(
            endpoint_id="endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(DedicatedEndpoint, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.with_raw_response.update(
                endpoint_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.list()
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.list(
            mine=True,
            type="dedicated",
            usage_type="on-demand",
        )
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(EndpointListResponse, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(EndpointListResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )
        assert endpoint is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert endpoint is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.delete(
            "endpoint-d23901de-ef8f-44bf-b3e7-de9c1ca8f2d7",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert endpoint is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_list_avzones(self, async_client: AsyncTogether) -> None:
        endpoint = await async_client.endpoints.list_avzones()
        assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

    @parametrize
    async def test_raw_response_list_avzones(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.with_raw_response.list_avzones()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endpoint = await response.parse()
        assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list_avzones(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.with_streaming_response.list_avzones() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endpoint = await response.parse()
            assert_matches_type(EndpointListAvzonesResponse, endpoint, path=["response"])

        assert cast(Any, response.is_closed) is True
