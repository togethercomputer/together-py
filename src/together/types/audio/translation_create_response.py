# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "TranslationCreateResponse",
    "AudioTranslationJsonResponse",
    "AudioTranslationVerboseJsonResponse",
    "AudioTranslationVerboseJsonResponseSegment",
    "AudioTranslationVerboseJsonResponseWord",
]


class AudioTranslationJsonResponse(BaseModel):
    text: str
    """The translated text"""


class AudioTranslationVerboseJsonResponseSegment(BaseModel):
    id: int
    """Unique identifier for the segment"""

    end: float
    """End time of the segment in seconds"""

    start: float
    """Start time of the segment in seconds"""

    text: str
    """The text content of the segment"""


class AudioTranslationVerboseJsonResponseWord(BaseModel):
    end: float
    """End time of the word in seconds"""

    start: float
    """Start time of the word in seconds"""

    word: str
    """The word"""

    speaker_id: Optional[str] = None
    """The speaker id for the word (only when diarize is enabled)"""


class AudioTranslationVerboseJsonResponse(BaseModel):
    duration: float
    """The duration of the audio in seconds"""

    language: str
    """The target language of the translation"""

    segments: List[AudioTranslationVerboseJsonResponseSegment]
    """Array of translation segments"""

    task: Literal["transcribe", "translate"]
    """The task performed"""

    text: str
    """The translated text"""

    words: Optional[List[AudioTranslationVerboseJsonResponseWord]] = None
    """Array of translation words (only when timestamp_granularities includes 'word')"""


TranslationCreateResponse: TypeAlias = Union[AudioTranslationJsonResponse, AudioTranslationVerboseJsonResponse]
