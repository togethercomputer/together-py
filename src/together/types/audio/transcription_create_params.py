# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, TypedDict

from ..._types import FileTypes

__all__ = ["TranscriptionCreateParams"]


class TranscriptionCreateParams(TypedDict, total=False):
    file: Required[Union[FileTypes, str]]
    """Audio file upload or public HTTP/HTTPS URL.

    Supported formats .wav, .mp3, .m4a, .webm, .flac.
    """

    diarize: bool
    """Whether to enable speaker diarization.

    When enabled, you will get the speaker id for each word in the transcription. In
    the response, in the words array, you will get the speaker id for each word. In
    addition, we also return the speaker_segments array which contains the speaker
    id for each speaker segment along with the start and end time of the segment
    along with all the words in the segment.

    For eg - ... "speaker_segments": [ "speaker_id": "SPEAKER_00", "start": 0,
    "end": 30.02, "words": [ { "id": 0, "word": "Tijana", "start": 0, "end": 11.475,
    "speaker_id": "SPEAKER_00" }, ...
    """

    language: str
    """Optional ISO 639-1 language code.

    If `auto` is provided, language is auto-detected.
    """

    max_speakers: int
    """Maximum number of speakers expected in the audio.

    Used to improve diarization accuracy when the approximate number of speakers is
    known.
    """

    min_speakers: int
    """Minimum number of speakers expected in the audio.

    Used to improve diarization accuracy when the approximate number of speakers is
    known.
    """

    model: Literal["openai/whisper-large-v3"]
    """Model to use for transcription"""

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
