# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    EvaluationListResponse,
    EvaluationRetrieveResponse,
    EvaluationGetStatusResponse,
    EvaluationGetAllowedModelsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        evaluation = client.evaluations.retrieve(
            "id",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.evaluations.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.evaluations.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: Together) -> None:
        evaluation = client.evaluations.list()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Together) -> None:
        evaluation = client.evaluations.list(
            limit=1,
            status="pending",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Together) -> None:
        response = client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Together) -> None:
        with client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_allowed_models(self, client: Together) -> None:
        evaluation = client.evaluations.get_allowed_models()
        assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_get_allowed_models(self, client: Together) -> None:
        response = client.evaluations.with_raw_response.get_allowed_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_get_allowed_models(self, client: Together) -> None:
        with client.evaluations.with_streaming_response.get_allowed_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Together) -> None:
        evaluation = client.evaluations.get_status(
            "id",
        )
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Together) -> None:
        response = client.evaluations.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Together) -> None:
        with client.evaluations.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get_status(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluations.with_raw_response.get_status(
                "",
            )


class TestAsyncEvaluations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluations.retrieve(
            "id",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluations.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluations.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluations.list()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluations.list(
            limit=1,
            status="pending",
        )
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationListResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_allowed_models(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluations.get_allowed_models()
        assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_get_allowed_models(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluations.with_raw_response.get_allowed_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_get_allowed_models(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluations.with_streaming_response.get_allowed_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationGetAllowedModelsResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluations.get_status(
            "id",
        )
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluations.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluations.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluations.with_raw_response.get_status(
                "",
            )
