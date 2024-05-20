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
    """
    If set, the response will contain the prompt, and will also return prompt
    logprobs if set with logprobs.
    """

    frequency_penalty: float
    """
    The `frequency_penalty` parameter is a number between -2.0 and 2.0 where a
    positive value will decrease the likelihood of repeating tokens that were
    mentioned prior.
    """

    logit_bias: Dict[str, object]
    """
    The `logit_bias` parameter allows us to adjust the likelihood of specific tokens
    appearing in the generated output.
    """

    logprobs: int
    """
    Determines the number of most likely tokens to return at each token position log
    probabilities to return
    """

    max_tokens: int
    """The maximum number of tokens to generate."""

    min_p: float
    """
    The `min_p` parameter is a number between 0 and 1 and an alternative to
    `temperature`.
    """

    n: int
    """Number of generations to return"""

    presence_penalty: float
    """
    The `presence_penalty` parameter is a number between -2.0 and 2.0 where a
    positive value will increase the likelihood of a model talking about new topics.
    """

    repetition_penalty: float
    """
    A number that controls the diversity of generated text by reducing the
    likelihood of repeated sequences. Higher values decrease repetition.
    """

    safety_model: str
    """The name of the safety model to use."""

    stop: List[str]
    """A list of string sequences that will truncate (stop) inference text output."""

    temperature: float
    """Determines the degree of randomness in the response."""

    top_k: int
    """
    The `top_k` parameter is used to limit the number of choices for the next
    predicted word or token.
    """

    top_p: float
    """
    The `top_p` (nucleus) parameter is used to dynamically adjust the number of
    choices for each predicted token based on the cumulative probabilities.
    """


class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase):
    stream: Literal[False]
    """If set, tokens are returned as Server-Sent Events as they are made available.

    Stream terminates with `data: [DONE]`
    """


class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Required[Literal[True]]
    """If set, tokens are returned as Server-Sent Events as they are made available.

    Stream terminates with `data: [DONE]`
    """


CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]
