# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "TranscriptionCreateResponse",
    "AudioTranscriptionJsonResponse",
    "AudioTranscriptionVerboseJsonResponse",
    "AudioTranscriptionVerboseJsonResponseSegment",
    "AudioTranscriptionVerboseJsonResponseSpeakerSegment",
    "AudioTranscriptionVerboseJsonResponseSpeakerSegmentWord",
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


class AudioTranscriptionVerboseJsonResponseSpeakerSegmentWord(BaseModel):
    end: float
    """End time of the word in seconds"""

    start: float
    """Start time of the word in seconds"""

    word: str
    """The word"""

    speaker_id: Optional[str] = None
    """The speaker id for the word (only when diarize is enabled)"""


class AudioTranscriptionVerboseJsonResponseSpeakerSegment(BaseModel):
    id: int
    """Unique identifier for the speaker segment"""

    end: float
    """End time of the speaker segment in seconds"""

    speaker_id: str
    """The speaker identifier"""

    start: float
    """Start time of the speaker segment in seconds"""

    text: str
    """The full text spoken by this speaker in this segment"""

    words: List[AudioTranscriptionVerboseJsonResponseSpeakerSegmentWord]
    """Array of words spoken by this speaker in this segment"""


class AudioTranscriptionVerboseJsonResponseWord(BaseModel):
    end: float
    """End time of the word in seconds"""

    start: float
    """Start time of the word in seconds"""

    word: str
    """The word"""

    speaker_id: Optional[str] = None
    """The speaker id for the word (only when diarize is enabled)"""


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

    speaker_segments: Optional[List[AudioTranscriptionVerboseJsonResponseSpeakerSegment]] = None
    """Array of transcription speaker segments (only when diarize is enabled)"""

    words: Optional[List[AudioTranscriptionVerboseJsonResponseWord]] = None
    """
    Array of transcription words (only when timestamp_granularities includes 'word')
    """


TranscriptionCreateResponse: TypeAlias = Union[AudioTranscriptionJsonResponse, AudioTranscriptionVerboseJsonResponse]
