# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import RerankCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRerank:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        rerank = client.rerank.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        )
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        rerank = client.rerank.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
            rank_fields=["title", "text"],
            return_documents=True,
            top_n=2,
        )
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.rerank.with_raw_response.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rerank = response.parse()
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.rerank.with_streaming_response.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rerank = response.parse()
            assert_matches_type(RerankCreateResponse, rerank, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRerank:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        rerank = await async_client.rerank.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        )
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        rerank = await async_client.rerank.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
            rank_fields=["title", "text"],
            return_documents=True,
            top_n=2,
        )
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.rerank.with_raw_response.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        rerank = await response.parse()
        assert_matches_type(RerankCreateResponse, rerank, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.rerank.with_streaming_response.create(
            documents=[
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
                {
                    "title": "bar",
                    "text": "bar",
                },
            ],
            model="Salesforce/Llama-Rank-V1",
            query="What animals can I find near Peru?",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            rerank = await response.parse()
            assert_matches_type(RerankCreateResponse, rerank, path=["response"])

        assert cast(Any, response.is_closed) is True
