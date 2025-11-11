# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    EvalListResponse,
    EvalRetrieveResponse,
    EvalGetStatusResponse,
    EvalGetAllowedModelsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        eval = client.evals.retrieve(
            "id",
        )
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.evals.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.evals.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evals.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        eval = client.evals.list()
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        eval = client.evals.list(
            limit=0,
            status="status",
            user_id="userId",
        )
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.evals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.evals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalListResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_allowed_models(self, client: Together) -> None:
        eval = client.evals.get_allowed_models()
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    def test_method_get_allowed_models_with_all_params(self, client: Together) -> None:
        eval = client.evals.get_allowed_models(
            model_source="model_source",
        )
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_get_allowed_models(self, client: Together) -> None:
        response = client.evals.with_raw_response.get_allowed_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_get_allowed_models(self, client: Together) -> None:
        with client.evals.with_streaming_response.get_allowed_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Together) -> None:
        eval = client.evals.get_status(
            "id",
        )
        assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Together) -> None:
        response = client.evals.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Together) -> None:
        with client.evals.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get_status(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evals.with_raw_response.get_status(
                "",
            )


class TestAsyncEvals:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.retrieve(
            "id",
        )
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evals.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.list()
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.list(
            limit=0,
            status="status",
            user_id="userId",
        )
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalListResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalListResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_allowed_models(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.get_allowed_models()
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    async def test_method_get_allowed_models_with_all_params(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.get_allowed_models(
            model_source="model_source",
        )
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_get_allowed_models(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.get_allowed_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_get_allowed_models(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.get_allowed_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalGetAllowedModelsResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.get_status(
            "id",
        )
        assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalGetStatusResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evals.with_raw_response.get_status(
                "",
            )
