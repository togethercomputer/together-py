# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CompletionCreateParamsBase", "CompletionCreateParamsNonStreaming", "CompletionCreateParamsStreaming"]


class CompletionCreateParamsBase(TypedDict, total=False):
    model: Required[str]
    """The name of the model to query."""

    prompt: Required[str]
    """A string providing context for the model to complete."""

    echo: bool
    """If true, the response will contain the prompt.

    Can be used with `logprobs` to return prompt logprobs.
    """

    frequency_penalty: float
    """
    A number between -2.0 and 2.0 where a positive value decreases the likelihood of
    repeating tokens that have already been mentioned.
    """

    logit_bias: Dict[str, float]
    """Adjusts the likelihood of specific tokens appearing in the generated output."""

    logprobs: int
    """
    Determines the number of most likely tokens to return at each token position log
    probabilities to return.
    """

    max_tokens: int
    """The maximum number of tokens to generate."""

    min_p: float
    """A number between 0 and 1 that can be used as an alternative to top-p and top-k."""

    n: int
    """The number of completions to generate for each prompt."""

    presence_penalty: float
    """
    A number between -2.0 and 2.0 where a positive value increases the likelihood of
    a model talking about new topics.
    """

    repetition_penalty: float
    """
    A number that controls the diversity of generated text by reducing the
    likelihood of repeated sequences. Higher values decrease repetition.
    """

    safety_model: str
    """The name of the moderation model used to validate tokens.

    Choose from the available moderation models found
    [here](https://docs.together.ai/docs/inference-models#moderation-models).
    """

    stop: List[str]
    """A list of string sequences that will truncate (stop) inference text output.

    For example, "</s>" will stop generation as soon as the model generates the
    given token.
    """

    temperature: float
    """
    A decimal number from 0-1 that determines the degree of randomness in the
    response. A temperature less than 1 favors more correctness and is appropriate
    for question answering or summarization. A value closer to 1 introduces more
    randomness in the output.
    """

    top_k: int
    """
    An integer that's used to limit the number of choices for the next predicted
    word or token. It specifies the maximum number of tokens to consider at each
    step, based on their probability of occurrence. This technique helps to speed up
    the generation process and can improve the quality of the generated text by
    focusing on the most likely options.
    """

    top_p: float
    """
    A percentage (also called the nucleus parameter) that's used to dynamically
    adjust the number of choices for each predicted token based on the cumulative
    probabilities. It specifies a probability threshold below which all less likely
    tokens are filtered out. This technique helps maintain diversity and generate
    more fluent and natural-sounding text.
    """


class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase):
    stream: Literal[False]
    """
    If true, stream tokens as Server-Sent Events as the model generates them instead
    of waiting for the full model response. The stream terminates with
    `data: [DONE]`. If false, return a single JSON object containing the results.
    """


class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Required[Literal[True]]
    """
    If true, stream tokens as Server-Sent Events as the model generates them instead
    of waiting for the full model response. The stream terminates with
    `data: [DONE]`. If false, return a single JSON object containing the results.
    """


CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]
