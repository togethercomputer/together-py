# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Mapping, cast
from typing_extensions import Literal, overload

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import extract_files, required_args, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ...types.audio import transcription_create_params
from ..._base_client import make_request_options
from ...types.audio_speech_stream_chunk import AudioSpeechStreamChunk
from ...types.audio.transcription_create_response import TranscriptionCreateResponse

__all__ = ["TranscriptionsResource", "AsyncTranscriptionsResource"]


class TranscriptionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TranscriptionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return TranscriptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranscriptionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return TranscriptionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Transcribes audio into text

        Args:
          file: Audio file to transcribe

          language: Optional ISO 639-1 language code. If `auto` is provided, language is
              auto-detected.

          model: Model to use for transcription

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Transcribes audio into text

        Args:
          file: Audio file to transcribe

          language: Optional ISO 639-1 language code. If `auto` is provided, language is
              auto-detected.

          model: Model to use for transcription

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["file"])
    def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse | Stream[AudioSpeechStreamChunk]:
        body = deepcopy_minimal(
            {
                "file": file,
                "language": language,
                "model": model,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timestamp_granularities": timestamp_granularities,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/audio/transcriptions",
            body=maybe_transform(body, transcription_create_params.TranscriptionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(
                Any, TranscriptionCreateResponse
            ),  # Union types cannot be passed in as arguments in the type system
            stream=stream or False,
            stream_cls=Stream[AudioSpeechStreamChunk],
        )


class AsyncTranscriptionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTranscriptionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTranscriptionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranscriptionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncTranscriptionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Transcribes audio into text

        Args:
          file: Audio file to transcribe

          language: Optional ISO 639-1 language code. If `auto` is provided, language is
              auto-detected.

          model: Model to use for transcription

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse:
        """
        Transcribes audio into text

        Args:
          file: Audio file to transcribe

          language: Optional ISO 639-1 language code. If `auto` is provided, language is
              auto-detected.

          model: Model to use for transcription

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["file"])
    async def create(
        self,
        *,
        file: FileTypes,
        language: str | NotGiven = NOT_GIVEN,
        model: Literal["openai/whisper-large-v3"] | NotGiven = NOT_GIVEN,
        prompt: str | NotGiven = NOT_GIVEN,
        response_format: Literal["json", "verbose_json"] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        timestamp_granularities: Literal["segment", "word"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TranscriptionCreateResponse | AsyncStream[AudioSpeechStreamChunk]:
        body = deepcopy_minimal(
            {
                "file": file,
                "language": language,
                "model": model,
                "prompt": prompt,
                "response_format": response_format,
                "temperature": temperature,
                "timestamp_granularities": timestamp_granularities,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/audio/transcriptions",
            body=await async_maybe_transform(body, transcription_create_params.TranscriptionCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(
                Any, TranscriptionCreateResponse
            ),  # Union types cannot be passed in as arguments in the type system
            stream=stream or False,
            stream_cls=AsyncStream[AudioSpeechStreamChunk],
        )


class TranscriptionsResourceWithRawResponse:
    def __init__(self, transcriptions: TranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = to_raw_response_wrapper(
            transcriptions.create,
        )


class AsyncTranscriptionsResourceWithRawResponse:
    def __init__(self, transcriptions: AsyncTranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = async_to_raw_response_wrapper(
            transcriptions.create,
        )


class TranscriptionsResourceWithStreamingResponse:
    def __init__(self, transcriptions: TranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = to_streamed_response_wrapper(
            transcriptions.create,
        )


class AsyncTranscriptionsResourceWithStreamingResponse:
    def __init__(self, transcriptions: AsyncTranscriptionsResource) -> None:
        self._transcriptions = transcriptions

        self.create = async_to_streamed_response_wrapper(
            transcriptions.create,
        )
