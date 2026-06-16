# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.endpoints import (
    AdapterAddResponse,
    AdapterListResponse,
    AdapterRemoveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdapters:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Together) -> None:
        adapter = client.endpoints.adapters.list(
            "endpointId",
        )
        assert_matches_type(AdapterListResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.endpoints.adapters.with_raw_response.list(
            "endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterListResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.endpoints.adapters.with_streaming_response.list(
            "endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterListResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.adapters.with_raw_response.list(
                "",
            )

    @parametrize
    def test_method_add(self, client: Together) -> None:
        adapter = client.endpoints.adapters.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        )
        assert_matches_type(AdapterAddResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_add(self, client: Together) -> None:
        response = client.endpoints.adapters.with_raw_response.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterAddResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_add(self, client: Together) -> None:
        with client.endpoints.adapters.with_streaming_response.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterAddResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_add(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.adapters.with_raw_response.add(
                endpoint_id="",
                model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
            )

    @parametrize
    def test_method_remove(self, client: Together) -> None:
        adapter = client.endpoints.adapters.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        )
        assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

    @parametrize
    def test_raw_response_remove(self, client: Together) -> None:
        response = client.endpoints.adapters.with_raw_response.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = response.parse()
        assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

    @parametrize
    def test_streaming_response_remove(self, client: Together) -> None:
        with client.endpoints.adapters.with_streaming_response.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = response.parse()
            assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_remove(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            client.endpoints.adapters.with_raw_response.remove(
                endpoint_id="",
                model_id="model_id",
            )


class TestAsyncAdapters:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.endpoints.adapters.list(
            "endpointId",
        )
        assert_matches_type(AdapterListResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.adapters.with_raw_response.list(
            "endpointId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterListResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.adapters.with_streaming_response.list(
            "endpointId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterListResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.adapters.with_raw_response.list(
                "",
            )

    @parametrize
    async def test_method_add(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.endpoints.adapters.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        )
        assert_matches_type(AdapterAddResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_add(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.adapters.with_raw_response.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterAddResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_add(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.adapters.with_streaming_response.add(
            endpoint_id="endpointId",
            model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterAddResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_add(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.adapters.with_raw_response.add(
                endpoint_id="",
                model_id="username/Meta-Llama-3.1-8B-Instruct-def456:username/my-adapter-abc123",
            )

    @parametrize
    async def test_method_remove(self, async_client: AsyncTogether) -> None:
        adapter = await async_client.endpoints.adapters.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        )
        assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

    @parametrize
    async def test_raw_response_remove(self, async_client: AsyncTogether) -> None:
        response = await async_client.endpoints.adapters.with_raw_response.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adapter = await response.parse()
        assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

    @parametrize
    async def test_streaming_response_remove(self, async_client: AsyncTogether) -> None:
        async with async_client.endpoints.adapters.with_streaming_response.remove(
            endpoint_id="endpointId",
            model_id="model_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adapter = await response.parse()
            assert_matches_type(AdapterRemoveResponse, adapter, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_remove(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `endpoint_id` but received ''"):
            await async_client.endpoints.adapters.with_raw_response.remove(
                endpoint_id="",
                model_id="model_id",
            )
