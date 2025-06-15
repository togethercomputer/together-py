# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AudioSpeechStreamChunk"]


class AudioSpeechStreamChunk(BaseModel):
    b64: str
    """base64 encoded audio stream"""

    model: str

    object: Literal["audio.tts.chunk"]
