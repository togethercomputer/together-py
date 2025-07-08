# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from ..._types import FileTypes

__all__ = ["TranscriptionCreateParams"]


class TranscriptionCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """Audio file to transcribe"""

    language: str
    """Optional ISO 639-1 language code.

    If `auto` is provided, language is auto-detected.
    """

    model: Literal["openai/whisper-large-v3"]
    """Model to use for transcription"""

    prompt: str
    """Optional text to bias decoding."""

    response_format: Literal["json", "verbose_json"]
    """The format of the response"""

    temperature: float
    """Sampling temperature between 0.0 and 1.0"""

    timestamp_granularities: Literal["segment", "word"]
    """Controls level of timestamp detail in verbose_json.

    Only used when response_format is verbose_json.
    """
