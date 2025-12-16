# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, TypedDict

from ..._types import FileTypes

__all__ = ["TranslationCreateParams"]


class TranslationCreateParams(TypedDict, total=False):
    file: Required[Union[FileTypes, str]]
    """Audio file upload or public HTTP/HTTPS URL.

    Supported formats .wav, .mp3, .m4a, .webm, .flac.
    """

    language: str
    """Target output language.

    Optional ISO 639-1 language code. If omitted, language is set to English.
    """

    model: Literal["openai/whisper-large-v3"]
    """Model to use for translation"""

    prompt: str
    """Optional text to bias decoding."""

    response_format: Literal["json", "verbose_json"]
    """The format of the response"""

    temperature: float
    """Sampling temperature between 0.0 and 1.0"""

    timestamp_granularities: Union[Literal["segment", "word"], List[Literal["segment", "word"]]]
    """Controls level of timestamp detail in verbose_json.

    Only used when response_format is verbose_json. Can be a single granularity or
    an array to get multiple levels.
    """
