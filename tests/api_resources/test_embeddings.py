# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types import Embedding

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEmbeddings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        embedding = client.embeddings.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        )
        assert_matches_type(Embedding, embedding, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.embeddings.with_raw_response.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(Embedding, embedding, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.embeddings.with_streaming_response.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = response.parse()
            assert_matches_type(Embedding, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEmbeddings:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        embedding = await async_client.embeddings.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        )
        assert_matches_type(Embedding, embedding, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.embeddings.with_raw_response.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = await response.parse()
        assert_matches_type(Embedding, embedding, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.embeddings.with_streaming_response.create(
            input="Our solar system orbits the Milky Way galaxy at about 515,000 mph",
            model="togethercomputer/m2-bert-80M-8k-retrieval",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = await response.parse()
            assert_matches_type(Embedding, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True
