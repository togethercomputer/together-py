# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, overload

import httpx

from ..types import completion_create_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import required_args, maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.completion import Completion
from ..types.completion_chunk import CompletionChunk

__all__ = ["CompletionsResource", "AsyncCompletionsResource"]


class CompletionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return CompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return CompletionsResourceWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        stream: Literal[True],
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[CompletionChunk]:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        stream: bool,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion | Stream[CompletionChunk]:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    def create(
        self,
        *,
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion | Stream[CompletionChunk]:
        return self._post(
            "/completions",
            body=maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "min_p": min_p,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "repetition_penalty": repetition_penalty,
                    "safety_model": safety_model,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Completion,
            stream=stream or False,
            stream_cls=Stream[CompletionChunk],
        )


class AsyncCompletionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/togethercomputer/together-py#accessing-raw-response-data-eg-headers
        """
        return AsyncCompletionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/togethercomputer/together-py#with_streaming_response
        """
        return AsyncCompletionsResourceWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        stream: Literal[False] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        stream: Literal[True],
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[CompletionChunk]:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        stream: bool,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion | AsyncStream[CompletionChunk]:
        """
        Query a language, code, or image model.

        Args:
          model: The name of the model to query.

              [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)

          prompt: A string providing context for the model to complete.

          stream: If true, stream tokens as Server-Sent Events as the model generates them instead
              of waiting for the full model response. The stream terminates with
              `data: [DONE]`. If false, return a single JSON object containing the results.

          echo: If true, the response will contain the prompt. Can be used with `logprobs` to
              return prompt logprobs.

          frequency_penalty: A number between -2.0 and 2.0 where a positive value decreases the likelihood of
              repeating tokens that have already been mentioned.

          logit_bias: Adjusts the likelihood of specific tokens appearing in the generated output.

          logprobs: An integer between 0 and 20 of the top k tokens to return log probabilities for
              at each generation step, instead of just the sampled token. Log probabilities
              help assess model confidence in token predictions.

          max_tokens: The maximum number of tokens to generate.

          min_p: A number between 0 and 1 that can be used as an alternative to top-p and top-k.

          n: The number of completions to generate for each prompt.

          presence_penalty: A number between -2.0 and 2.0 where a positive value increases the likelihood of
              a model talking about new topics.

          repetition_penalty: A number that controls the diversity of generated text by reducing the
              likelihood of repeated sequences. Higher values decrease repetition.

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

    @required_args(["model", "prompt"], ["model", "prompt", "stream"])
    async def create(
        self,
        *,
        model: Union[
            Literal[
                "meta-llama/Llama-2-70b-hf",
                "mistralai/Mistral-7B-v0.1",
                "mistralai/Mixtral-8x7B-v0.1",
                "Meta-Llama/Llama-Guard-7b",
            ],
            str,
        ],
        prompt: str,
        echo: bool | Omit = omit,
        frequency_penalty: float | Omit = omit,
        logit_bias: Dict[str, float] | Omit = omit,
        logprobs: int | Omit = omit,
        max_tokens: int | Omit = omit,
        min_p: float | Omit = omit,
        n: int | Omit = omit,
        presence_penalty: float | Omit = omit,
        repetition_penalty: float | Omit = omit,
        safety_model: Union[Literal["Meta-Llama/Llama-Guard-7b"], str] | Omit = omit,
        seed: int | Omit = omit,
        stop: SequenceNotStr[str] | Omit = omit,
        stream: Literal[False] | Literal[True] | Omit = omit,
        temperature: float | Omit = omit,
        top_k: int | Omit = omit,
        top_p: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Completion | AsyncStream[CompletionChunk]:
        return await self._post(
            "/completions",
            body=await async_maybe_transform(
                {
                    "model": model,
                    "prompt": prompt,
                    "echo": echo,
                    "frequency_penalty": frequency_penalty,
                    "logit_bias": logit_bias,
                    "logprobs": logprobs,
                    "max_tokens": max_tokens,
                    "min_p": min_p,
                    "n": n,
                    "presence_penalty": presence_penalty,
                    "repetition_penalty": repetition_penalty,
                    "safety_model": safety_model,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                },
                completion_create_params.CompletionCreateParamsStreaming
                if stream
                else completion_create_params.CompletionCreateParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Completion,
            stream=stream or False,
            stream_cls=AsyncStream[CompletionChunk],
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
