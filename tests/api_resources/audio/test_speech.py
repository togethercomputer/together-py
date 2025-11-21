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


class TestSpeech:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_overload_1(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        )
        assert speech.is_closed
        assert speech.json() == {"foo": "bar"}
        assert cast(Any, speech.is_closed) is True
        assert isinstance(speech, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_with_all_params_overload_1(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
            stream=False,
        )
        assert speech.is_closed
        assert speech.json() == {"foo": "bar"}
        assert cast(Any, speech.is_closed) is True
        assert isinstance(speech, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create_overload_1(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        speech = client.audio.speech.with_raw_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        )

        assert speech.is_closed is True
        assert speech.http_request.headers.get("X-Stainless-Lang") == "python"
        assert speech.json() == {"foo": "bar"}
        assert isinstance(speech, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create_overload_1(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.audio.speech.with_streaming_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        ) as speech:
            assert not speech.is_closed
            assert speech.http_request.headers.get("X-Stainless-Lang") == "python"

            assert speech.json() == {"foo": "bar"}
            assert cast(Any, speech.is_closed) is True
            assert isinstance(speech, StreamedBinaryAPIResponse)

        assert cast(Any, speech.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_overload_2(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech_stream = client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        )
        speech_stream.response.close()

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_with_all_params_overload_2(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech_stream = client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
        )
        speech_stream.response.close()

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create_overload_2(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        speech_stream = client.audio.speech.with_raw_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        )

        assert speech_stream.http_request.headers.get("X-Stainless-Lang") == "python"
        assert speech_stream.json() == {"foo": "bar"}
        assert isinstance(speech_stream, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create_overload_2(self, client: Together, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.audio.speech.with_streaming_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        ) as speech_stream:
            assert not speech_stream.is_closed
            assert speech_stream.http_request.headers.get("X-Stainless-Lang") == "python"

            assert speech_stream.json() == {"foo": "bar"}
            assert cast(Any, speech_stream.is_closed) is True
            assert isinstance(speech_stream, StreamedBinaryAPIResponse)

        assert cast(Any, speech_stream.is_closed) is True


class TestAsyncSpeech:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_overload_1(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await async_client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        )
        assert speech.is_closed
        assert await speech.json() == {"foo": "bar"}
        assert cast(Any, speech.is_closed) is True
        assert isinstance(speech, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params_overload_1(
        self, async_client: AsyncTogether, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech = await async_client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
            stream=False,
        )
        assert speech.is_closed
        assert await speech.json() == {"foo": "bar"}
        assert cast(Any, speech.is_closed) is True
        assert isinstance(speech, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create_overload_1(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        speech = await async_client.audio.speech.with_raw_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        )

        assert speech.is_closed is True
        assert speech.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await speech.json() == {"foo": "bar"}
        assert isinstance(speech, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create_overload_1(
        self, async_client: AsyncTogether, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.audio.speech.with_streaming_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            voice="voice",
        ) as speech:
            assert not speech.is_closed
            assert speech.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await speech.json() == {"foo": "bar"}
            assert cast(Any, speech.is_closed) is True
            assert isinstance(speech, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, speech.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_overload_2(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech_stream = await async_client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        )
        await speech_stream.response.aclose()

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_with_all_params_overload_2(
        self, async_client: AsyncTogether, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        speech_stream = await async_client.audio.speech.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
            language="en",
            response_encoding="pcm_f32le",
            response_format="mp3",
            sample_rate=0,
        )
        await speech_stream.response.aclose()

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create_overload_2(self, async_client: AsyncTogether, respx_mock: MockRouter) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        speech_stream = await async_client.audio.speech.with_raw_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        )

        assert speech_stream.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await speech_stream.json() == {"foo": "bar"}
        assert isinstance(speech_stream, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create_overload_2(
        self, async_client: AsyncTogether, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/audio/speech").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.audio.speech.with_streaming_response.create(
            input="input",
            model="canopylabs/orpheus-3b-0.1-ft",
            stream=True,
            voice="voice",
        ) as speech_stream:
            assert not speech_stream.is_closed
            assert speech_stream.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await speech_stream.json() == {"foo": "bar"}
            assert cast(Any, speech_stream.is_closed) is True
            assert isinstance(speech_stream, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, speech_stream.is_closed) is True
