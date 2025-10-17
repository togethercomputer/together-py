# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import EvaluationRetrieveResponse, EvaluationGetStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvaluation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")    
    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        evaluation = client.evaluation.retrieve(
            "id",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.evaluation.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.evaluation.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_path_params_retrieve(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluation.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_method_get_status(self, client: Together) -> None:
        evaluation = client.evaluation.get_status(
            "id",
        )
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_raw_response_get_status(self, client: Together) -> None:
        response = client.evaluation.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = response.parse()
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_streaming_response_get_status(self, client: Together) -> None:
        with client.evaluation.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = response.parse()
            assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    def test_path_params_get_status(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evaluation.with_raw_response.get_status(
                "",
            )


class TestAsyncEvaluation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluation.retrieve(
            "id",
        )
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluation.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluation.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationRetrieveResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluation.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_method_get_status(self, async_client: AsyncTogether) -> None:
        evaluation = await async_client.evaluation.get_status(
            "id",
        )
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.evaluation.with_raw_response.get_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        evaluation = await response.parse()
        assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncTogether) -> None:
        async with async_client.evaluation.with_streaming_response.get_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            evaluation = await response.parse()
            assert_matches_type(EvaluationGetStatusResponse, evaluation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled") 
    @parametrize
    async def test_path_params_get_status(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evaluation.with_raw_response.get_status(
                "",
            )
