# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from together import Together, AsyncTogether
from tests.utils import assert_matches_type
from together.types.audio import TranscriptionCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTranscriptions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Together) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Together) -> None:
        transcription = client.audio.transcriptions.create(
            file=b"raw file contents",
            diarize=True,
            language="en",
            max_speakers=0,
            min_speakers=0,
            model="openai/whisper-large-v3",
            prompt="prompt",
            response_format="json",
            temperature=0,
            timestamp_granularities=["word", "segment"],
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Together) -> None:
        response = client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = response.parse()
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Together) -> None:
        with client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = response.parse()
            assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTranscriptions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncTogether) -> None:
        transcription = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTogether) -> None:
        transcription = await async_client.audio.transcriptions.create(
            file=b"raw file contents",
            diarize=True,
            language="en",
            max_speakers=0,
            min_speakers=0,
            model="openai/whisper-large-v3",
            prompt="prompt",
            response_format="json",
            temperature=0,
            timestamp_granularities=["word", "segment"],
        )
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTogether) -> None:
        response = await async_client.audio.transcriptions.with_raw_response.create(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        transcription = await response.parse()
        assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTogether) -> None:
        async with async_client.audio.transcriptions.with_streaming_response.create(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            transcription = await response.parse()
            assert_matches_type(TranscriptionCreateResponse, transcription, path=["response"])

        assert cast(Any, response.is_closed) is True
