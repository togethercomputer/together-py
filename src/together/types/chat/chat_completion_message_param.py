# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..tool_choice_param import ToolChoiceParam
from .chat_completion_tool_message_param import ChatCompletionToolMessageParam
from .chat_completion_system_message_param import ChatCompletionSystemMessageParam
from .chat_completion_function_message_param import ChatCompletionFunctionMessageParam
from .chat_completion_structured_message_text_param import ChatCompletionStructuredMessageTextParam
from .chat_completion_structured_message_image_url_param import ChatCompletionStructuredMessageImageURLParam
from .chat_completion_structured_message_video_url_param import ChatCompletionStructuredMessageVideoURLParam

__all__ = [
    "ChatCompletionMessageParam",
    "ChatCompletionUserMessageParam",
    "ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal",
    "ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio",
    "ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL",
    "ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio",
    "ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio",
    "ChatCompletionAssistantMessageParam",
    "ChatCompletionAssistantMessageParamFunctionCall",
]


class ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL(
    TypedDict, total=False
):
    url: Required[str]
    """The URL of the audio"""


class ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio(TypedDict, total=False):
    audio_url: Required[ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudioAudioURL]

    type: Required[Literal["audio_url"]]


class ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio(
    TypedDict, total=False
):
    data: Required[str]
    """The base64 encoded audio data"""

    format: Required[Literal["wav"]]
    """The format of the audio data"""


class ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio(TypedDict, total=False):
    input_audio: Required[
        ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio
    ]

    type: Required[Literal["input_audio"]]


ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal: TypeAlias = Union[
    ChatCompletionStructuredMessageTextParam,
    ChatCompletionStructuredMessageImageURLParam,
    ChatCompletionStructuredMessageVideoURLParam,
    ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalAudio,
    ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodalInputAudio,
]


class ChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[
        Union[str, Iterable[ChatCompletionUserMessageParamContentChatCompletionUserMessageContentMultimodal]]
    ]
    """
    The content of the message, which can either be a simple string or a structured
    format.
    """

    role: Required[Literal["user"]]

    name: str


class ChatCompletionAssistantMessageParamFunctionCall(TypedDict, total=False):
    arguments: Required[str]

    name: Required[str]


class ChatCompletionAssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]

    content: Optional[str]

    function_call: ChatCompletionAssistantMessageParamFunctionCall

    name: str

    tool_calls: Iterable[ToolChoiceParam]


ChatCompletionMessageParam: TypeAlias = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
]
