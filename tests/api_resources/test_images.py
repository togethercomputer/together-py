# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import ImageFile

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestImages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        image = client.images.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        )
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        image = client.images.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
            height=0,
            image_url="image_url",
            n=0,
            negative_prompt="negative_prompt",
            response_format="base64",
            seed=0,
            steps=0,
            width=0,
        )
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.images.with_raw_response.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.images.with_streaming_response.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImageFile, image, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncImages:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        image = await async_client.images.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        )
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        image = await async_client.images.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
            height=0,
            image_url="image_url",
            n=0,
            negative_prompt="negative_prompt",
            response_format="base64",
            seed=0,
            steps=0,
            width=0,
        )
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.images.with_raw_response.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = await response.parse()
        assert_matches_type(ImageFile, image, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.images.with_streaming_response.create(
            model="black-forest-labs/FLUX.1-schnell-Free",
            prompt="cat floating in space, cinematic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImageFile, image, path=["response"])

        assert cast(Any, response.is_closed) is True
