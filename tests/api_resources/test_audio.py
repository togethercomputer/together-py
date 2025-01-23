# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from together import Together, AsyncTogether
from together._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAudio:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        audio = client.audio.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        )
        assert audio.is_closed
        assert audio.json() == {"foo": "bar"}
        assert cast(Any, audio.is_closed) is True
        assert isinstance(audio, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_with_all_params(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        audio = client.audio.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
            stream=True,
        )
        assert audio.is_closed
        assert audio.json() == {"foo": "bar"}
        assert cast(Any, audio.is_closed) is True
        assert isinstance(audio, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        audio = client.audio.with_raw_response.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        )

        assert audio.is_closed is True
        assert audio.http_request.headers.get("X-Stainless-Lang") == "python"
        assert audio.json() == {"foo": "bar"}
        assert isinstance(audio, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.audio.with_streaming_response.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        ) as audio:
            assert not audio.is_closed
            assert audio.http_request.headers.get("X-Stainless-Lang") == "python"

            assert audio.json() == {"foo": "bar"}
            assert cast(Any, audio.is_closed) is True
            assert isinstance(audio, StreamedBinaryAPIResponse)

        assert cast(Any, audio.is_closed) is True


class TestAsyncAudio:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        audio = await async_client.audio.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        )
        assert audio.is_closed
        assert await audio.json() == {"foo": "bar"}
        assert cast(Any, audio.is_closed) is True
        assert isinstance(audio, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        audio = await async_client.audio.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
            stream=True,
        )
        assert audio.is_closed
        assert await audio.json() == {"foo": "bar"}
        assert cast(Any, audio.is_closed) is True
        assert isinstance(audio, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        audio = await async_client.audio.with_raw_response.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        )

        assert audio.is_closed is True
        assert audio.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await audio.json() == {"foo": "bar"}
        assert isinstance(audio, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.audio.with_streaming_response.create(
            input="input",
            model="cartesia/sonic",
            voice="laidback woman",
        ) as audio:
            assert not audio.is_closed
            assert audio.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await audio.json() == {"foo": "bar"}
            assert cast(Any, audio.is_closed) is True
            assert isinstance(audio, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, audio.is_closed) is True
