# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.pagination import SyncCursorPagination, AsyncCursorPagination
from together.types.beta.models import Config

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConfigs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        config = client.beta.models.configs.retrieve(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Config, config, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.beta.models.configs.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(Config, config, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.beta.models.configs.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(Config, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.models.configs.with_raw_response.retrieve(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.beta.models.configs.with_raw_response.retrieve(
                id="",
                project_id="projectId",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        config = client.beta.models.configs.list(
            project_id="projectId",
        )
        assert_matches_type(SyncCursorPagination[Config], config, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        config = client.beta.models.configs.list(
            project_id="projectId",
            after="after",
            limit=0,
            reference_model="referenceModel",
            reference_model_id="referenceModelId",
        )
        assert_matches_type(SyncCursorPagination[Config], config, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.beta.models.configs.with_raw_response.list(
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = response.parse()
        assert_matches_type(SyncCursorPagination[Config], config, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.beta.models.configs.with_streaming_response.list(
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = response.parse()
            assert_matches_type(SyncCursorPagination[Config], config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.beta.models.configs.with_raw_response.list(
                project_id="",
            )


class TestAsyncConfigs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        config = await async_client.beta.models.configs.retrieve(
            id="id",
            project_id="projectId",
        )
        assert_matches_type(Config, config, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.models.configs.with_raw_response.retrieve(
            id="id",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(Config, config, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.models.configs.with_streaming_response.retrieve(
            id="id",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(Config, config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.models.configs.with_raw_response.retrieve(
                id="id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.beta.models.configs.with_raw_response.retrieve(
                id="",
                project_id="projectId",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        config = await async_client.beta.models.configs.list(
            project_id="projectId",
        )
        assert_matches_type(AsyncCursorPagination[Config], config, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        config = await async_client.beta.models.configs.list(
            project_id="projectId",
            after="after",
            limit=0,
            reference_model="referenceModel",
            reference_model_id="referenceModelId",
        )
        assert_matches_type(AsyncCursorPagination[Config], config, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.beta.models.configs.with_raw_response.list(
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        config = await response.parse()
        assert_matches_type(AsyncCursorPagination[Config], config, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.beta.models.configs.with_streaming_response.list(
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            config = await response.parse()
            assert_matches_type(AsyncCursorPagination[Config], config, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.beta.models.configs.with_raw_response.list(
                project_id="",
            )
