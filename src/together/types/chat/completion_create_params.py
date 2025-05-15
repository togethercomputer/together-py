# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..tools_param import ToolsParam
from ..tool_choice_param import ToolChoiceParam

__all__ = [
    "CompletionCreateParamsBase",
    "Message",
    "MessageChatCompletionSystemMessageParam",
    "MessageChatCompletionUserMessageParam",
    "MessageChatCompletionAssistantMessageParam",
    "MessageChatCompletionAssistantMessageParamFunctionCall",
    "MessageChatCompletionToolMessageParam",
    "MessageChatCompletionFunctionMessageParam",
    "FunctionCall",
    "FunctionCallName",
    "ResponseFormat",
    "ToolChoice",
    "CompletionCreateParamsNonStreaming",
    "CompletionCreateParamsStreaming",
]


class CompletionCreateParamsBase(TypedDict, total=False):
    messages: Required[Iterable[Message]]
    """A list of messages comprising the conversation so far."""

    model: Required[
        Union[
            Literal[
                "Qwen/Qwen2.5-72B-Instruct-Turbo",
                "Qwen/Qwen2.5-7B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            ],
            str,
        ]
    ]
    """The name of the model to query.

    [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#chat-models)
    """

    context_length_exceeded_behavior: Literal["truncate", "error"]
    """
    Defined the behavior of the API when max_tokens exceed the maximum context
    length of the model. When set to 'error', API will return 400 with appropriate
    error message. When set to 'truncate', override the max_tokens with maximum
    context length of the model.
    """

    echo: bool
    """If true, the response will contain the prompt.

    Can be used with `logprobs` to return prompt logprobs.
    """

    frequency_penalty: float
    """
    A number between -2.0 and 2.0 where a positive value decreases the likelihood of
    repeating tokens that have already been mentioned.
    """

    function_call: FunctionCall

    logit_bias: Dict[str, float]
    """Adjusts the likelihood of specific tokens appearing in the generated output."""

    logprobs: int
    """
    Integer (0 or 1) that controls whether log probabilities of generated tokens are
    returned. Log probabilities help assess model confidence in token predictions.
    """

    max_tokens: int
    """The maximum number of tokens to generate."""

    min_p: float
    """A number between 0 and 1 that can be used as an alternative to top_p and top-k."""

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

    response_format: ResponseFormat
    """An object specifying the format that the model must output."""

    safety_model: str
    """The name of the moderation model used to validate tokens.

    Choose from the available moderation models found
    [here](https://docs.together.ai/docs/inference-models#moderation-models).
    """

    seed: int
    """Seed value for reproducibility."""

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

    tool_choice: ToolChoice
    """Controls which (if any) function is called by the model.

    By default uses `auto`, which lets the model pick between generating a message
    or calling a function.
    """

    tools: Iterable[ToolsParam]
    """A list of tools the model may call.

    Currently, only functions are supported as a tool. Use this to provide a list of
    functions the model may generate JSON inputs for.
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


class MessageChatCompletionSystemMessageParam(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["system"]]

    name: str


class MessageChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["user"]]

    name: str


class MessageChatCompletionAssistantMessageParamFunctionCall(TypedDict, total=False):
    arguments: Required[str]

    name: Required[str]


class MessageChatCompletionAssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]

    content: Optional[str]

    function_call: MessageChatCompletionAssistantMessageParamFunctionCall

    name: str

    tool_calls: Iterable[ToolChoiceParam]


class MessageChatCompletionToolMessageParam(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["tool"]]

    tool_call_id: Required[str]


class MessageChatCompletionFunctionMessageParam(TypedDict, total=False):
    content: Required[str]

    name: Required[str]

    role: Required[Literal["function"]]


Message: TypeAlias = Union[
    MessageChatCompletionSystemMessageParam,
    MessageChatCompletionUserMessageParam,
    MessageChatCompletionAssistantMessageParam,
    MessageChatCompletionToolMessageParam,
    MessageChatCompletionFunctionMessageParam,
]


class FunctionCallName(TypedDict, total=False):
    name: Required[str]


FunctionCall: TypeAlias = Union[Literal["none", "auto"], FunctionCallName]


class ResponseFormat(TypedDict, total=False):
    schema: Dict[str, object]
    """The schema of the response format."""

    type: str
    """The type of the response format."""


ToolChoice: TypeAlias = Union[str, ToolChoiceParam]


class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase, total=False):
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
