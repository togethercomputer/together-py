# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, overload

import httpx

from ..types import audio_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_raw_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.audio_speech_stream_chunk import AudioSpeechStreamChunk

__all__ = ["AudioResource", "AsyncAudioResource"]


class AudioResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AudioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AudioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AudioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AudioResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

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
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        stream: Literal[True],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

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
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        stream: bool,
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse | Stream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input", "model", "voice"], ["input", "model", "stream", "voice"])
    def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse | Stream[AudioSpeechStreamChunk]:
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            "/audio/speech",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "voice": voice,
                    "language": language,
                    "response_encoding": response_encoding,
                    "response_format": response_format,
                    "sample_rate": sample_rate,
                    "stream": stream,
                },
                audio_create_params.AudioCreateParamsStreaming
                if stream
                else audio_create_params.AudioCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
            stream=stream or False,
            stream_cls=Stream[AudioSpeechStreamChunk],
        )


class AsyncAudioResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAudioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncAudioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAudioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncAudioResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

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
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        stream: Literal[True],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

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
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        stream: bool,
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse | AsyncStream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text

          response_encoding: Audio encoding of response

          response_format: The format of audio output

          sample_rate: Sampling rate to use for the output audio

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input", "model", "voice"], ["input", "model", "stream", "voice"])
    async def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic"], str],
        voice: Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str],
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | NotGiven = NOT_GIVEN,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "wav", "raw"] | NotGiven = NOT_GIVEN,
        sample_rate: float | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse | AsyncStream[AudioSpeechStreamChunk]:
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._post(
            "/audio/speech",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "voice": voice,
                    "language": language,
                    "response_encoding": response_encoding,
                    "response_format": response_format,
                    "sample_rate": sample_rate,
                    "stream": stream,
                },
                audio_create_params.AudioCreateParamsStreaming
                if stream
                else audio_create_params.AudioCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
            stream=stream or False,
            stream_cls=AsyncStream[AudioSpeechStreamChunk],
        )


class AudioResourceWithRawResponse:
    def __init__(self, audio: AudioResource) -> None:
        self._audio = audio

        self.create = to_custom_raw_response_wrapper(
            audio.create,
            BinaryAPIResponse,
        )


class AsyncAudioResourceWithRawResponse:
    def __init__(self, audio: AsyncAudioResource) -> None:
        self._audio = audio

        self.create = async_to_custom_raw_response_wrapper(
            audio.create,
            AsyncBinaryAPIResponse,
        )


class AudioResourceWithStreamingResponse:
    def __init__(self, audio: AudioResource) -> None:
        self._audio = audio

        self.create = to_custom_streamed_response_wrapper(
            audio.create,
            StreamedBinaryAPIResponse,
        )


class AsyncAudioResourceWithStreamingResponse:
    def __init__(self, audio: AsyncAudioResource) -> None:
        self._audio = audio

        self.create = async_to_custom_streamed_response_wrapper(
            audio.create,
            AsyncStreamedBinaryAPIResponse,
        )
