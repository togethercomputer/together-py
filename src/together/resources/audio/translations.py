# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Union, Mapping, cast
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, FileTypes, omit, not_given
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.audio import translation_create_params
from ..._base_client import make_request_options
from ...types.audio.translation_create_response import TranslationCreateResponse

__all__ = ["TranslationsResource", "AsyncTranslationsResource"]


class TranslationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TranslationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return TranslationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TranslationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return TranslationsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        file: Union[FileTypes, str],
        language: str | Omit = omit,
        model: Literal["openai/whisper-large-v3"] | Omit = omit,
        prompt: str | Omit = omit,
        response_format: Literal["json", "verbose_json"] | Omit = omit,
        temperature: float | Omit = omit,
        timestamp_granularities: Union[Literal["segment", "word"], List[Literal["segment", "word"]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslationCreateResponse:
        """
        Translates audio into English

        Args:
          file: Audio file upload or public HTTP/HTTPS URL. Supported formats .wav, .mp3, .m4a,
              .webm, .flac.

          language: Target output language. Optional ISO 639-1 language code. If omitted, language
              is set to English.

          model: Model to use for translation

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json. Can be a single granularity or an array to get
              multiple levels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
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
        return cast(
            TranslationCreateResponse,
            self._post(
                "/audio/translations",
                body=maybe_transform(body, translation_create_params.TranslationCreateParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, TranslationCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncTranslationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTranslationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncTranslationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTranslationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncTranslationsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: Union[FileTypes, str],
        language: str | Omit = omit,
        model: Literal["openai/whisper-large-v3"] | Omit = omit,
        prompt: str | Omit = omit,
        response_format: Literal["json", "verbose_json"] | Omit = omit,
        temperature: float | Omit = omit,
        timestamp_granularities: Union[Literal["segment", "word"], List[Literal["segment", "word"]]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TranslationCreateResponse:
        """
        Translates audio into English

        Args:
          file: Audio file upload or public HTTP/HTTPS URL. Supported formats .wav, .mp3, .m4a,
              .webm, .flac.

          language: Target output language. Optional ISO 639-1 language code. If omitted, language
              is set to English.

          model: Model to use for translation

          prompt: Optional text to bias decoding.

          response_format: The format of the response

          temperature: Sampling temperature between 0.0 and 1.0

          timestamp_granularities: Controls level of timestamp detail in verbose_json. Only used when
              response_format is verbose_json. Can be a single granularity or an array to get
              multiple levels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
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
        return cast(
            TranslationCreateResponse,
            await self._post(
                "/audio/translations",
                body=await async_maybe_transform(body, translation_create_params.TranslationCreateParams),
                files=files,
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, TranslationCreateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class TranslationsResourceWithRawResponse:
    def __init__(self, translations: TranslationsResource) -> None:
        self._translations = translations

        self.create = to_raw_response_wrapper(
            translations.create,
        )


class AsyncTranslationsResourceWithRawResponse:
    def __init__(self, translations: AsyncTranslationsResource) -> None:
        self._translations = translations

        self.create = async_to_raw_response_wrapper(
            translations.create,
        )


class TranslationsResourceWithStreamingResponse:
    def __init__(self, translations: TranslationsResource) -> None:
        self._translations = translations

        self.create = to_streamed_response_wrapper(
            translations.create,
        )


class AsyncTranslationsResourceWithStreamingResponse:
    def __init__(self, translations: AsyncTranslationsResource) -> None:
        self._translations = translations

        self.create = async_to_streamed_response_wrapper(
            translations.create,
        )
