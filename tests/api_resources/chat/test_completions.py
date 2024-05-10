# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from together_ai import TogetherAI, AsyncTogetherAI
from together_ai.types.chat import ChatCompletion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: TogetherAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: TogetherAI) -> None:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            echo=True,
            frequency_penalty=0,
            logit_bias={
                "105": 21.4,
                "1024": -10.5,
            },
            logprobs=0,
            max_tokens=0,
            min_p=0,
            n=1,
            presence_penalty=0,
            repetition_penalty=0,
            response_format={
                "type": "json",
                "schema": {},
            },
            safety_model="safety_model_name",
            stop=["string", "string", "string"],
            stream=False,
            temperature=0,
            tool_choice="tool_name",
            tools=[
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_k=0,
            top_p=0,
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: TogetherAI) -> None:
        response = client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: TogetherAI) -> None:
        with client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: TogetherAI) -> None:
        completion_stream = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        )
        completion_stream.response.close()

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: TogetherAI) -> None:
        completion_stream = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
            echo=True,
            frequency_penalty=0,
            logit_bias={
                "105": 21.4,
                "1024": -10.5,
            },
            logprobs=0,
            max_tokens=0,
            min_p=0,
            n=1,
            presence_penalty=0,
            repetition_penalty=0,
            response_format={
                "type": "json",
                "schema": {},
            },
            safety_model="safety_model_name",
            stop=["string", "string", "string"],
            temperature=0,
            tool_choice="tool_name",
            tools=[
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_k=0,
            top_p=0,
        )
        completion_stream.response.close()

    @parametrize
    def test_raw_response_create_overload_2(self, client: TogetherAI) -> None:
        response = client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_create_overload_2(self, client: TogetherAI) -> None:
        with client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncTogetherAI) -> None:
        completion = await async_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncTogetherAI) -> None:
        completion = await async_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            echo=True,
            frequency_penalty=0,
            logit_bias={
                "105": 21.4,
                "1024": -10.5,
            },
            logprobs=0,
            max_tokens=0,
            min_p=0,
            n=1,
            presence_penalty=0,
            repetition_penalty=0,
            response_format={
                "type": "json",
                "schema": {},
            },
            safety_model="safety_model_name",
            stop=["string", "string", "string"],
            stream=False,
            temperature=0,
            tool_choice="tool_name",
            tools=[
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_k=0,
            top_p=0,
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncTogetherAI) -> None:
        response = await async_client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncTogetherAI) -> None:
        async with async_client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncTogetherAI) -> None:
        completion_stream = await async_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        )
        await completion_stream.response.aclose()

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncTogetherAI) -> None:
        completion_stream = await async_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
            echo=True,
            frequency_penalty=0,
            logit_bias={
                "105": 21.4,
                "1024": -10.5,
            },
            logprobs=0,
            max_tokens=0,
            min_p=0,
            n=1,
            presence_penalty=0,
            repetition_penalty=0,
            response_format={
                "type": "json",
                "schema": {},
            },
            safety_model="safety_model_name",
            stop=["string", "string", "string"],
            temperature=0,
            tool_choice="tool_name",
            tools=[
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
                {
                    "type": "tool_type",
                    "function": {
                        "description": "A description of the function.",
                        "name": "function_name",
                        "parameters": {"foo": "bar"},
                    },
                },
            ],
            top_k=0,
            top_p=0,
        )
        await completion_stream.response.aclose()

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncTogetherAI) -> None:
        response = await async_client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncTogetherAI) -> None:
        async with async_client.chat.completions.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
