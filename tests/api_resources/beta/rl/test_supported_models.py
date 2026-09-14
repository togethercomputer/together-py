# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.rl import RlSupportedModels

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSupportedModels:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get(self, client: Together) -> None:
        supported_model = client.beta.rl.supported_models.get()
        assert_matches_type(RlSupportedModels, supported_model, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Together) -> None:
        response = client.beta.rl.supported_models.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supported_model = response.parse()
        assert_matches_type(RlSupportedModels, supported_model, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Together) -> None:
        with client.beta.rl.supported_models.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supported_model = response.parse()
            assert_matches_type(RlSupportedModels, supported_model, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSupportedModels:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_get(self, async_client: AsyncTogether) -> None:
        supported_model = await async_client.beta.rl.supported_models.get()
        assert_matches_type(RlSupportedModels, supported_model, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.rl.supported_models.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        supported_model = await response.parse()
        assert_matches_type(RlSupportedModels, supported_model, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.rl.supported_models.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            supported_model = await response.parse()
            assert_matches_type(RlSupportedModels, supported_model, path=["response"])

        assert cast(Any, response.is_closed) is True
