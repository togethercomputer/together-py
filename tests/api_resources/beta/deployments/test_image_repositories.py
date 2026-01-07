# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.beta.deployments import ImageRepositoryListResponse, ImageRepositoryRetrieveImagesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestImageRepositories:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Together) -> None:
        image_repository = client.beta.deployments.image_repositories.list()
        assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.deployments.image_repositories.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_repository = response.parse()
        assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.deployments.image_repositories.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_repository = response.parse()
            assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve_images(self, client: Together) -> None:
        image_repository = client.beta.deployments.image_repositories.retrieve_images(
            "id",
        )
        assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

    @parametrize
    def test_raw_response_retrieve_images(self, client: Together) -> None:
        response = client.beta.deployments.image_repositories.with_raw_response.retrieve_images(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_repository = response.parse()
        assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

    @parametrize
    def test_streaming_response_retrieve_images(self, client: Together) -> None:
        with client.beta.deployments.image_repositories.with_streaming_response.retrieve_images(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_repository = response.parse()
            assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve_images(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.deployments.image_repositories.with_raw_response.retrieve_images(
                "",
            )


class TestAsyncImageRepositories:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        image_repository = await async_client.beta.deployments.image_repositories.list()
        assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.image_repositories.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_repository = await response.parse()
        assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.image_repositories.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_repository = await response.parse()
            assert_matches_type(ImageRepositoryListResponse, image_repository, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve_images(self, async_client: AsyncTogether) -> None:
        image_repository = await async_client.beta.deployments.image_repositories.retrieve_images(
            "id",
        )
        assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_images(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.deployments.image_repositories.with_raw_response.retrieve_images(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image_repository = await response.parse()
        assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve_images(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.deployments.image_repositories.with_streaming_response.retrieve_images(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image_repository = await response.parse()
            assert_matches_type(ImageRepositoryRetrieveImagesResponse, image_repository, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve_images(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.deployments.image_repositories.with_raw_response.retrieve_images(
                "",
            )
