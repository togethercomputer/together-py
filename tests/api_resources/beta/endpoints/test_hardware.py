# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.endpoints import HardwareListResponse, InferenceInstanceType

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHardware:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        hardware = client.beta.endpoints.hardware.retrieve(
            "id",
        )
        assert_matches_type(InferenceInstanceType, hardware, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.endpoints.hardware.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hardware = response.parse()
        assert_matches_type(InferenceInstanceType, hardware, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.endpoints.hardware.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hardware = response.parse()
            assert_matches_type(InferenceInstanceType, hardware, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.endpoints.hardware.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        hardware = client.beta.endpoints.hardware.list()
        assert_matches_type(HardwareListResponse, hardware, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.endpoints.hardware.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hardware = response.parse()
        assert_matches_type(HardwareListResponse, hardware, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.endpoints.hardware.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hardware = response.parse()
            assert_matches_type(HardwareListResponse, hardware, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncHardware:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        hardware = await async_client.beta.endpoints.hardware.retrieve(
            "id",
        )
        assert_matches_type(InferenceInstanceType, hardware, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.hardware.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hardware = await response.parse()
        assert_matches_type(InferenceInstanceType, hardware, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.hardware.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hardware = await response.parse()
            assert_matches_type(InferenceInstanceType, hardware, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.endpoints.hardware.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        hardware = await async_client.beta.endpoints.hardware.list()
        assert_matches_type(HardwareListResponse, hardware, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.endpoints.hardware.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        hardware = await response.parse()
        assert_matches_type(HardwareListResponse, hardware, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.endpoints.hardware.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            hardware = await response.parse()
            assert_matches_type(HardwareListResponse, hardware, path=["response"])

        assert cast(Any, response.is_closed) is True
