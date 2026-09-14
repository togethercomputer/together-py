# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionStructuredMessageVideoURLParam", "VideoURL"]


class VideoURL(TypedDict, total=False):
    url: Required[str]
    """The URL of the video"""


class ChatCompletionStructuredMessageVideoURLParam(TypedDict, total=False):
    type: Required[Literal["video_url"]]

    video_url: Required[VideoURL]
