# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from together_ai.types import CompletionResponse

from typing import Any, cast

import os
import pytest
import httpx
from typing_extensions import get_args
from typing import Optional
from respx import MockRouter
from together_ai import TogetherAI, AsyncTogetherAI
from tests.utils import assert_matches_type
from together_ai.types import completion_create_params

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=['loose', 'strict'])


    @parametrize
    def test_method_create(self, client: TogetherAI) -> None:
        completion = client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        )
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    def test_method_create_with_all_params(self, client: TogetherAI) -> None:
        completion = client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
            echo=True,
            logprobs=0,
            max_tokens=0,
            n=1,
            repetition_penalty=0,
            stop=["string", "string", "string"],
            stream=True,
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    def test_raw_response_create(self, client: TogetherAI) -> None:

        response = client.completions.with_raw_response.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get('X-Stainless-Lang') == 'python'
        completion = response.parse()
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    def test_streaming_response_create(self, client: TogetherAI) -> None:
        with client.completions.with_streaming_response.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        ) as response :
            assert not response.is_closed
            assert response.http_request.headers.get('X-Stainless-Lang') == 'python'

            completion = response.parse()
            assert_matches_type(CompletionResponse, completion, path=['response'])

        assert cast(Any, response.is_closed) is True
class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=['loose', 'strict'])


    @parametrize
    async def test_method_create(self, async_client: AsyncTogetherAI) -> None:
        completion = await async_client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        )
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogetherAI) -> None:
        completion = await async_client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
            echo=True,
            logprobs=0,
            max_tokens=0,
            n=1,
            repetition_penalty=0,
            stop=["string", "string", "string"],
            stream=True,
            temperature=0,
            top_k=0,
            top_p=0,
        )
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogetherAI) -> None:

        response = await async_client.completions.with_raw_response.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get('X-Stainless-Lang') == 'python'
        completion = await response.parse()
        assert_matches_type(CompletionResponse, completion, path=['response'])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogetherAI) -> None:
        async with async_client.completions.with_streaming_response.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt="<s>[INST] What is the capital of France? [/INST]",
        ) as response :
            assert not response.is_closed
            assert response.http_request.headers.get('X-Stainless-Lang') == 'python'

            completion = await response.parse()
            assert_matches_type(CompletionResponse, completion, path=['response'])

        assert cast(Any, response.is_closed) is True