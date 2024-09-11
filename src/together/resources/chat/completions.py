# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable, overload
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    required_args,
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._streaming import Stream, AsyncStream
from ...types.chat import completion_create_params
from ..._base_client import make_request_options
from ...types.tools_param import ToolsParam
from ...types.chat.chat_completion import ChatCompletion
from ...types.chat.chat_completion_chunk import ChatCompletionChunk

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

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
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: Literal[True],
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[ChatCompletionChunk]:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

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
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: bool,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        return self._post(
            "/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "min_p": min_p,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "repetition_penalty": repetition_penalty,
                    "response_format": response_format,
                    "safety_model": safety_model,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletion,
            stream=stream or False,
            stream_cls=Stream[ChatCompletionChunk],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

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
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: Literal[True],
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[ChatCompletionChunk]:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

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
        messages: Iterable[completion_create_params.Message],
        model: str,
        stream: bool,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk]:
        """
        Query a chat model.

        Args:
          messages: A list of messages comprising the conversation so far.

          model: The name of the model to query.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: Determines the number of most likely tokens to return at each token position log
              probabilities to return.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top_p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

          response_format: An object specifying the format that the model must output.

          safety_model: The name of the moderation model used to validate tokens. Choose from the
              available moderation models found
              [here](https://docs.together.ai/docs/inference-models#moderation-models).

          seed: Seed value for reproducibility.

          stop: A list of string sequences that will truncate (stop) inference text output. For
              example, "</s>" will stop generation as soon as the model generates the given
              token.

          temperature: A decimal number from 0-1 that determines the degree of randomness in the
              response. A temperature less than 1 favors more correctness and is appropriate
              for question answering or summarization. A value closer to 1 introduces more
              randomness in the output.

          tool_choice: Controls which (if any) function is called by the model. By default uses `auto`,
              which lets the model pick between generating a message or calling a function.

          tools: A list of tools the model may call. Currently, only functions are supported as a
              tool. Use this to provide a list of functions the model may generate JSON inputs
              for.

          top_k: An integer that's used to limit the number of choices for the next predicted
              word or token. It specifies the maximum number of tokens to consider at each
              step, based on their probability of occurrence. This technique helps to speed up
              the generation process and can improve the quality of the generated text by
              focusing on the most likely options.

          top_p: A percentage (also called the nucleus parameter) that's used to dynamically
              adjust the number of choices for each predicted token based on the cumulative
              probabilities. It specifies a probability threshold below which all less likely
              tokens are filtered out. This technique helps maintain diversity and generate
              more fluent and natural-sounding text.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: str,
        echo: bool | NotGiven = NOT_GIVEN,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        logit_bias: Dict[str, float] | NotGiven = NOT_GIVEN,
        logprobs: int | NotGiven = NOT_GIVEN,
        max_tokens: int | NotGiven = NOT_GIVEN,
        min_p: float | NotGiven = NOT_GIVEN,
        n: int | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        repetition_penalty: float | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        safety_model: str | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: List[str] | NotGiven = NOT_GIVEN,
        stream: Literal[False] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: float | NotGiven = NOT_GIVEN,
        tool_choice: completion_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolsParam] | NotGiven = NOT_GIVEN,
        top_k: int | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk]:
        return await self._post(
            "/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "function_call": function_call,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "min_p": min_p,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "repetition_penalty": repetition_penalty,
                    "response_format": response_format,
                    "safety_model": safety_model,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletion,
            stream=stream or False,
            stream_cls=AsyncStream[ChatCompletionChunk],
        )


class CompletionsResourceWithRawResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_raw_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithRawResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_raw_response_wrapper(
            completions.create,
        )


class CompletionsResourceWithStreamingResponse:
    def __init__(self, completions: CompletionsResource) -> None:
        self._completions = completions

        self.create = to_streamed_response_wrapper(
            completions.create,
        )


class AsyncCompletionsResourceWithStreamingResponse:
    def __init__(self, completions: AsyncCompletionsResource) -> None:
        self._completions = completions

        self.create = async_to_streamed_response_wrapper(
            completions.create,
        )
