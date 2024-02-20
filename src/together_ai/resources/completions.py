# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import httpx

from .._compat import cached_property

from ..types import CompletionResponse

from typing import List

from .._response import to_raw_response_wrapper, async_to_raw_response_wrapper, to_streamed_response_wrapper, async_to_streamed_response_wrapper

import warnings
from typing import TYPE_CHECKING, Optional, Union, List, Dict, Any, Mapping, cast, overload
from typing_extensions import Literal
from .._utils import extract_files, maybe_transform, required_args, deepcopy_minimal, strip_not_given
from .._types import NotGiven, Timeout, Headers, NoneType, Query, Body, NOT_GIVEN, FileTypes, BinaryResponseContent
from .._resource import SyncAPIResource, AsyncAPIResource
from .._base_client import SyncAPIClient, AsyncAPIClient, _merge_mappings, AsyncPaginator, make_request_options, HttpxBinaryResponseContent
from ..types import shared_params
from ..types import completion_create_params

__all__ = ["Completions", "AsyncCompletions"]

class Completions(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsWithRawResponse:
        return CompletionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsWithStreamingResponse:
        return CompletionsWithStreamingResponse(self)

    def create(self,
    *,
    model: str,
    prompt: str,
    echo: bool | NotGiven = NOT_GIVEN,
    logprobs: int | NotGiven = NOT_GIVEN,
    max_tokens: int | NotGiven = NOT_GIVEN,
    n: int | NotGiven = NOT_GIVEN,
    repetition_penalty: float | NotGiven = NOT_GIVEN,
    stop: List[str] | NotGiven = NOT_GIVEN,
    stream: bool | NotGiven = NOT_GIVEN,
    temperature: float | NotGiven = NOT_GIVEN,
    top_k: int | NotGiven = NOT_GIVEN,
    top_p: float | NotGiven = NOT_GIVEN,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,) -> CompletionResponse:
        """
        Creates a completion for the provided prompt and parameters

        Args:
          model: The name of the model to query.

          prompt: A string providing context for the model to complete.

          echo: If set, the response will contain the prompt, and will also return prompt
              logprobs if set with logprobs.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return

          max_tokens: The maximum number of tokens to generate.

          n: Number of generations to return

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          stop: A list of string sequences that will truncate (stop) inference text output.

          stream: If set, tokens are returned as Server-Sent Events as they are made available.
              Stream terminates with `data: [DONE]`

          temperature: Determines the degree of randomness in the response.

          top_k: The `top_k` parameter is used to limit the number of choices for the next
              predicted word or token.

          top_p: The `top_p` (nucleus) parameter is used to dynamically adjust the number of
              choices for each predicted token based on the cumulative probabilities.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/completions",
            body=maybe_transform({
                "model": model,
                "prompt": prompt,
                "echo": echo,
                "logprobs": logprobs,
                "max_tokens": max_tokens,
                "n": n,
                "repetition_penalty": repetition_penalty,
                "stop": stop,
                "stream": stream,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
            }, completion_create_params.CompletionCreateParams),
            options=make_request_options(extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout),
            cast_to=CompletionResponse,
        )

class AsyncCompletions(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsWithRawResponse:
        return AsyncCompletionsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsWithStreamingResponse:
        return AsyncCompletionsWithStreamingResponse(self)

    async def create(self,
    *,
    model: str,
    prompt: str,
    echo: bool | NotGiven = NOT_GIVEN,
    logprobs: int | NotGiven = NOT_GIVEN,
    max_tokens: int | NotGiven = NOT_GIVEN,
    n: int | NotGiven = NOT_GIVEN,
    repetition_penalty: float | NotGiven = NOT_GIVEN,
    stop: List[str] | NotGiven = NOT_GIVEN,
    stream: bool | NotGiven = NOT_GIVEN,
    temperature: float | NotGiven = NOT_GIVEN,
    top_k: int | NotGiven = NOT_GIVEN,
    top_p: float | NotGiven = NOT_GIVEN,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,) -> CompletionResponse:
        """
        Creates a completion for the provided prompt and parameters

        Args:
          model: The name of the model to query.

          prompt: A string providing context for the model to complete.

          echo: If set, the response will contain the prompt, and will also return prompt
              logprobs if set with logprobs.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return

          max_tokens: The maximum number of tokens to generate.

          n: Number of generations to return

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          stop: A list of string sequences that will truncate (stop) inference text output.

          stream: If set, tokens are returned as Server-Sent Events as they are made available.
              Stream terminates with `data: [DONE]`

          temperature: Determines the degree of randomness in the response.

          top_k: The `top_k` parameter is used to limit the number of choices for the next
              predicted word or token.

          top_p: The `top_p` (nucleus) parameter is used to dynamically adjust the number of
              choices for each predicted token based on the cumulative probabilities.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/completions",
            body=maybe_transform({
                "model": model,
                "prompt": prompt,
                "echo": echo,
                "logprobs": logprobs,
                "max_tokens": max_tokens,
                "n": n,
                "repetition_penalty": repetition_penalty,
                "stop": stop,
                "stream": stream,
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
            }, completion_create_params.CompletionCreateParams),
            options=make_request_options(extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout),
            cast_to=CompletionResponse,
        )

class CompletionsWithRawResponse:
    def __init__(self, completions: Completions) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )

class AsyncCompletionsWithRawResponse:
    def __init__(self, completions: AsyncCompletions) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )

class CompletionsWithStreamingResponse:
    def __init__(self, completions: Completions) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )

class AsyncCompletionsWithStreamingResponse:
    def __init__(self, completions: AsyncCompletions) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )