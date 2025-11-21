# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, overload

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..._utils import required_args, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_raw_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ...types.audio import speech_create_params
from ..._base_client import make_request_options
from ...types.audio_speech_stream_chunk import AudioSpeechStreamChunk

__all__ = ["SpeechResource", "AsyncSpeechResource"]


class SpeechResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SpeechResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return SpeechResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SpeechResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return SpeechResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        stream: Literal[False] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        stream: Literal[True],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        stream: bool,
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse | Stream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
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
                speech_create_params.SpeechCreateParamsStreaming
                if stream
                else speech_create_params.SpeechCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
            stream=stream or False,
            stream_cls=Stream[AudioSpeechStreamChunk],
        )


class AsyncSpeechResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSpeechResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncSpeechResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSpeechResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncSpeechResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        input: str,
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        stream: Literal[False] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        stream: Literal[True],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        stream: bool,
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse | AsyncStream[AudioSpeechStreamChunk]:
        """
        Generate audio from input text

        Args:
          input: Input text to generate the audio for

          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
              The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
              canopylabs/orpheus-3b-0.1-ft

          stream: If true, output is streamed for several characters at a time instead of waiting
              for the full response. The stream terminates with `data: [DONE]`. If false,
              return the encoded audio as octet stream

          voice: The voice to use for generating the audio. The voices supported are different
              for each model. For eg - for canopylabs/orpheus-3b-0.1-ft, one of the voices
              supported is tara, for hexgrad/Kokoro-82M, one of the voices supported is
              af_alloy and for cartesia/sonic, one of the voices supported is "friendly
              sidekick".

              You can view the voices supported for each model using the /v1/voices endpoint
              sending the model name as the query parameter.
              [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).

          language: Language of input text.

          response_encoding: Audio encoding of response

          response_format: The format of audio output. Supported formats are mp3, wav, raw if streaming is
              false. If streaming is true, the only supported format is raw.

          sample_rate: Sampling rate to use for the output audio. The default sampling rate for
              canopylabs/orpheus-3b-0.1-ft and hexgrad/Kokoro-82M is 24000 and for
              cartesia/sonic is 44100.

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
        model: Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str],
        voice: str,
        language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
        | Omit = omit,
        response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"] | Omit = omit,
        response_format: Literal["mp3", "wav", "raw"] | Omit = omit,
        sample_rate: int | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
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
                speech_create_params.SpeechCreateParamsStreaming
                if stream
                else speech_create_params.SpeechCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
            stream=stream or False,
            stream_cls=AsyncStream[AudioSpeechStreamChunk],
        )


class SpeechResourceWithRawResponse:
    def __init__(self, speech: SpeechResource) -> None:
        self._speech = speech

        self.create = to_custom_raw_response_wrapper(
            speech.create,
            BinaryAPIResponse,
        )


class AsyncSpeechResourceWithRawResponse:
    def __init__(self, speech: AsyncSpeechResource) -> None:
        self._speech = speech

        self.create = async_to_custom_raw_response_wrapper(
            speech.create,
            AsyncBinaryAPIResponse,
        )


class SpeechResourceWithStreamingResponse:
    def __init__(self, speech: SpeechResource) -> None:
        self._speech = speech

        self.create = to_custom_streamed_response_wrapper(
            speech.create,
            StreamedBinaryAPIResponse,
        )


class AsyncSpeechResourceWithStreamingResponse:
    def __init__(self, speech: AsyncSpeechResource) -> None:
        self._speech = speech

        self.create = async_to_custom_streamed_response_wrapper(
            speech.create,
            AsyncStreamedBinaryAPIResponse,
        )
