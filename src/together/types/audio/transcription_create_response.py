# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "TranscriptionCreateResponse",
    "AudioTranscriptionJsonResponse",
    "AudioTranscriptionVerboseJsonResponse",
    "AudioTranscriptionVerboseJsonResponseSegment",
    "AudioTranscriptionVerboseJsonResponseWord",
]


class AudioTranscriptionJsonResponse(BaseModel):
    text: str
    """The transcribed text"""


class AudioTranscriptionVerboseJsonResponseSegment(BaseModel):
    id: int
    """Unique identifier for the segment"""

    end: float
    """End time of the segment in seconds"""

    start: float
    """Start time of the segment in seconds"""

    text: str
    """The text content of the segment"""

    tokens: List[int]
    """Array of token IDs for the segment"""


class AudioTranscriptionVerboseJsonResponseWord(BaseModel):
    end: float
    """End time of the word in seconds"""

    start: float
    """Start time of the word in seconds"""

    word: str
    """The word"""


class AudioTranscriptionVerboseJsonResponse(BaseModel):
    duration: float
    """The duration of the audio in seconds"""

    language: str
    """The language of the audio"""

    segments: List[AudioTranscriptionVerboseJsonResponseSegment]
    """Array of transcription segments"""

    task: Literal["transcribe", "translate"]
    """The task performed"""

    text: str
    """The transcribed text"""

    words: Optional[List[AudioTranscriptionVerboseJsonResponseWord]] = None
    """
    Array of transcription words (only when timestamp_granularities includes 'word')
    """


TranscriptionCreateResponse: TypeAlias = Union[AudioTranscriptionJsonResponse, AudioTranscriptionVerboseJsonResponse]
