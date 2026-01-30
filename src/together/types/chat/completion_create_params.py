# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..._types import SequenceNotStr
from ..tools_param import ToolsParam
from ..tool_choice_param import ToolChoiceParam
from .chat_completion_structured_message_text_param import ChatCompletionStructuredMessageTextParam
from .chat_completion_structured_message_image_url_param import ChatCompletionStructuredMessageImageURLParam
from .chat_completion_structured_message_video_url_param import ChatCompletionStructuredMessageVideoURLParam

__all__ = [
    "CompletionCreateParamsBase",
    "Message",
    "MessageChatCompletionSystemMessageParam",
    "MessageChatCompletionUserMessageParam",
    "MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal",
    "MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio",
    "MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL",
    "MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio",
    "MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio",
    "MessageChatCompletionAssistantMessageParam",
    "MessageChatCompletionAssistantMessageParamFunctionCall",
    "MessageChatCompletionToolMessageParam",
    "MessageChatCompletionFunctionMessageParam",
    "FunctionCall",
    "FunctionCallName",
    "Reasoning",
    "ResponseFormat",
    "ResponseFormatText",
    "ResponseFormatJsonSchema",
    "ResponseFormatJsonSchemaJsonSchema",
    "ResponseFormatJsonObject",
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

    chat_template_kwargs: object

    compliance: Literal["hipaa"]

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
    An integer between 0 and 20 of the top k tokens to return log probabilities for
    at each generation step, instead of just the sampled token. Log probabilities
    help assess model confidence in token predictions.
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

    reasoning: Reasoning

    reasoning_effort: Literal["low", "medium", "high"]
    """
    Controls the level of reasoning effort the model should apply when generating
    responses. Higher values may result in more thoughtful and detailed responses
    but may take longer to generate.
    """

    repetition_penalty: float
    """
    A number that controls the diversity of generated text by reducing the
    likelihood of repeated sequences. Higher values decrease repetition.
    """

    response_format: ResponseFormat
    """An object specifying the format that the model must output.

    Setting to `{ "type": "json_schema", "json_schema": {...} }` enables Structured
    Outputs which ensures the model will match your supplied JSON schema. Learn more
    in the [Structured Outputs guide](https://docs.together.ai/docs/json-mode).

    Setting to `{ "type": "json_object" }` enables the older JSON mode, which
    ensures the message the model generates is valid JSON. Using `json_schema` is
    preferred for models that support it.
    """

    safety_model: str
    """The name of the moderation model used to validate tokens.

    Choose from the available moderation models found
    [here](https://docs.together.ai/docs/inference-models#moderation-models).
    """

    seed: int
    """Seed value for reproducibility."""

    stop: SequenceNotStr[str]
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


class MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL(
    TypedDict, total=False
):
    url: Required[str]
    """The URL of the audio"""


class MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio(
    TypedDict, total=False
):
    audio_url: Required[
        MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL
    ]

    type: Required[Literal["audio_url"]]


class MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio(
    TypedDict, total=False
):
    data: Required[str]
    """The base64 encoded audio data"""

    format: Required[Literal["wav"]]
    """The format of the audio data"""


class MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio(
    TypedDict, total=False
):
    input_audio: Required[
        MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio
    ]

    type: Required[Literal["input_audio"]]


MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal: TypeAlias = Union[
    ChatCompletionStructuredMessageTextParam,
    ChatCompletionStructuredMessageImageURLParam,
    ChatCompletionStructuredMessageVideoURLParam,
    MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio,
    MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio,
]


class MessageChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[
        Union[str, Iterable[MessageChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal]]
    ]
    """
    The content of the message, which can either be a simple string or a structured
    format.
    """

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

    name: str


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


class Reasoning(TypedDict, total=False):
    enabled: bool
    """
    For models that support toggling reasoning functionality, this object can be
    used to control that functionality.
    """


class ResponseFormatText(TypedDict, total=False):
    """Default response format. Used to generate text responses."""

    type: Required[Literal["text"]]
    """The type of response format being defined. Always `text`."""


class ResponseFormatJsonSchemaJsonSchema(TypedDict, total=False):
    """Structured Outputs configuration options, including a JSON Schema."""

    name: Required[str]
    """The name of the response format.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: str
    """
    A description of what the response format is for, used by the model to determine
    how to respond in the format.
    """

    schema: Dict[str, object]
    """
    The schema for the response format, described as a JSON Schema object. Learn how
    to build JSON schemas [here](https://json-schema.org/).
    """

    strict: Optional[bool]
    """
    Whether to enable strict schema adherence when generating the output. If set to
    true, the model will always follow the exact schema defined in the `schema`
    field. Only a subset of JSON Schema is supported when `strict` is `true`. To
    learn more, read the
    [Structured Outputs guide](https://docs.together.ai/docs/json-mode).
    """


class ResponseFormatJsonSchema(TypedDict, total=False):
    """JSON Schema response format.

    Used to generate structured JSON responses.
    Learn more about [Structured Outputs](https://docs.together.ai/docs/json-mode).
    """

    json_schema: Required[ResponseFormatJsonSchemaJsonSchema]
    """Structured Outputs configuration options, including a JSON Schema."""

    type: Required[Literal["json_schema"]]
    """The type of response format being defined. Always `json_schema`."""


class ResponseFormatJsonObject(TypedDict, total=False):
    """JSON object response format.

    An older method of generating JSON responses.
    Using `json_schema` is recommended for models that support it. Note that the
    model will not generate JSON without a system or user message instructing it
    to do so.
    """

    type: Required[Literal["json_object"]]
    """The type of response format being defined. Always `json_object`."""


ResponseFormat: TypeAlias = Union[ResponseFormatText, ResponseFormatJsonSchema, ResponseFormatJsonObject]

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
