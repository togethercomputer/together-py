# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import (
    EvaluationJob,
    EvalListResponse,
    EvalCreateResponse,
    EvalStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    def test_method_create(self, client: Together) -> None:
        eval = client.evals.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        eval = client.evals.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                    "external_api_token": "external_api_token",
                    "external_base_url": "external_base_url",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
                "model_to_evaluate": "string",
            },
            type="classify",
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.evals.with_raw_response.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.evals.with_streaming_response.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalCreateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: Together) -> None:
        eval = client.evals.retrieve(
            "id",
        )
        assert_matches_type(EvaluationJob, eval, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Together) -> None:
        response = client.evals.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvaluationJob, eval, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Together) -> None:
        with client.evals.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvaluationJob, eval, path=["response"])

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
    def test_method_status(self, client: Together) -> None:
        eval = client.evals.status(
            "id",
        )
        assert_matches_type(EvalStatusResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_status(self, client: Together) -> None:
        response = client.evals.with_raw_response.status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalStatusResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_status(self, client: Together) -> None:
        with client.evals.with_streaming_response.status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalStatusResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_status(self, client: Together) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.evals.with_raw_response.status(
                "",
            )


class TestAsyncEvals:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                    "external_api_token": "external_api_token",
                    "external_base_url": "external_base_url",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
                "model_to_evaluate": "string",
            },
            type="classify",
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @pytest.mark.skip(reason="Skipping evals tests atm")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.create(
            parameters={
                "input_data_file_path": "file-1234-aefd",
                "judge": {
                    "model": "meta-llama/Llama-3-70B-Instruct-Turbo",
                    "model_source": "serverless",
                    "system_template": "Imagine you are a helpful assistant",
                },
                "labels": ["yes", "no"],
                "pass_labels": ["yes"],
            },
            type="classify",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalCreateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.retrieve(
            "id",
        )
        assert_matches_type(EvaluationJob, eval, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvaluationJob, eval, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvaluationJob, eval, path=["response"])

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
    async def test_method_status(self, async_client: AsyncTogether) -> None:
        eval = await async_client.evals.status(
            "id",
        )
        assert_matches_type(EvalStatusResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_status(self, async_client: AsyncTogether) -> None:
        response = await async_client.evals.with_raw_response.status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = await response.parse()
        assert_matches_type(EvalStatusResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_status(self, async_client: AsyncTogether) -> None:
        async with async_client.evals.with_streaming_response.status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalStatusResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_status(self, async_client: AsyncTogether) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.evals.with_raw_response.status(
                "",
            )
