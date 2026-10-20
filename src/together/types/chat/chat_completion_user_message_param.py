# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .chat_completion_structured_message_text_param import ChatCompletionStructuredMessageTextParam
from .chat_completion_structured_message_image_url_param import ChatCompletionStructuredMessageImageURLParam
from .chat_completion_structured_message_video_url_param import ChatCompletionStructuredMessageVideoURLParam

__all__ = [
    "ChatCompletionUserMessageParam",
    "ContentChatCompletionUserMessageContentMultimodal",
    "ContentChatCompletionUserMessageContentMultimodalAudio",
    "ContentChatCompletionUserMessageContentMultimodalAudioAudioURL",
    "ContentChatCompletionUserMessageContentMultimodalInputAudio",
    "ContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio",
]


class ContentChatCompletionUserMessageContentMultimodalAudioAudioURL(TypedDict, total=False):
    url: Required[str]
    """The URL of the audio"""


class ContentChatCompletionUserMessageContentMultimodalAudio(TypedDict, total=False):
    audio_url: Required[ContentChatCompletionUserMessageContentMultimodalAudioAudioURL]

    type: Required[Literal["audio_url"]]


class ContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio(TypedDict, total=False):
    data: Required[str]
    """The base64 encoded audio data"""

    format: Required[Literal["wav"]]
    """The format of the audio data"""


class ContentChatCompletionUserMessageContentMultimodalInputAudio(TypedDict, total=False):
    input_audio: Required[ContentChatCompletionUserMessageContentMultimodalInputAudioInputAudio]

    type: Required[Literal["input_audio"]]


ContentChatCompletionUserMessageContentMultimodal: TypeAlias = Union[
    ChatCompletionStructuredMessageTextParam,
    ChatCompletionStructuredMessageImageURLParam,
    ChatCompletionStructuredMessageVideoURLParam,
    ContentChatCompletionUserMessageContentMultimodalAudio,
    ContentChatCompletionUserMessageContentMultimodalInputAudio,
]


class ChatCompletionUserMessageParam(TypedDict, total=False):
    content: Required[Union[str, Iterable[ContentChatCompletionUserMessageContentMultimodal]]]
    """
    The content of the message, which can either be a simple string or a structured
    format.
    """

    role: Required[Literal["user"]]

    name: str
