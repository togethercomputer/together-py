# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import List
from typing_extensions import Required, TypedDict

__all__ = ["CompletionCreateParams"]


class CompletionCreateParams(TypedDict, total=False):
    model: Required[str]
    """The name of the model to query."""

    prompt: Required[str]
    """A string providing context for the model to complete."""

    echo: bool
    """
    If set, the response will contain the prompt, and will also return prompt
    logprobs if set with logprobs.
    """

    logprobs: int
    """
    Determines the number of most likely tokens to return at each token position log
    probabilities to return
    """

    max_tokens: int
    """The maximum number of tokens to generate."""

    n: int
    """Number of generations to return"""

    repetition_penalty: float
    """
    A number that controls the diversity of generated text by reducing the
    likelihood of repeated sequences. Higher values decrease repetition.
    """

    stop: List[str]
    """A list of string sequences that will truncate (stop) inference text output."""

    stream: bool
    """If set, tokens are returned as Server-Sent Events as they are made available.

    Stream terminates with `data: [DONE]`
    """

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
