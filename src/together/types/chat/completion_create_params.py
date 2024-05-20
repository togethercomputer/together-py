# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, TypedDict

from ..tools_param import ToolsParam
from ..tool_choice_param import ToolChoiceParam

__all__ = [
    "CompletionCreateParamsBase",
    "Message",
    "ResponseFormat",
    "ToolChoice",
    "CompletionCreateParamsNonStreaming",
    "CompletionCreateParamsStreaming",
]


class CompletionCreateParamsBase(TypedDict, total=False):
    messages: Required[Iterable[Message]]
    """A list of messages comprising the conversation so far."""

    model: Required[str]
    """The name of the model to query."""

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

    logit_bias: Dict[str, str]
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

    response_format: ResponseFormat
    """Specifies the format of the response."""

    safety_model: str
    """The name of the safety model to use."""

    stop: List[str]
    """A list of string sequences that will truncate (stop) inference text output."""

    temperature: float
    """Determines the degree of randomness in the response."""

    tool_choice: ToolChoice
    """The choice of tool to use."""

    tools: Iterable[ToolsParam]
    """A list of tools to be used in the query."""

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


class Message(TypedDict, total=False):
    content: Required[str]
    """The contents of the message."""

    role: Required[Literal["system", "user", "assistant"]]
    """The role of the messages author. Choice between: system, user, or assistant."""


class ResponseFormat(TypedDict, total=False):
    schema: Dict[str, str]
    """The schema of the response format."""

    type: str
    """The type of the response format."""


ToolChoice = Union[str, ToolChoiceParam]


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
