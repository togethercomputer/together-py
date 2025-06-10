# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["AudioCreateParamsBase", "AudioCreateParamsNonStreaming", "AudioCreateParamsStreaming"]


class AudioCreateParamsBase(TypedDict, total=False):
    input: Required[str]
    """Input text to generate the audio for"""

    model: Required[Union[Literal["cartesia/sonic"], str]]
    """The name of the model to query.

    [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
    """

    voice: Required[Union[Literal["laidback woman", "polite man", "storyteller lady", "friendly sidekick"], str]]
    """The voice to use for generating the audio.

    [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).
    """

    language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
    """Language of input text"""

    response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"]
    """Audio encoding of response"""

    response_format: Literal["mp3", "wav", "raw"]
    """The format of audio output"""

    sample_rate: float
    """Sampling rate to use for the output audio"""


class AudioCreateParamsNonStreaming(AudioCreateParamsBase, total=False):
    stream: Literal[False]
    """
    If true, output is streamed for several characters at a time instead of waiting
    for the full response. The stream terminates with `data: [DONE]`. If false,
    return the encoded audio as octet stream
    """


class AudioCreateParamsStreaming(AudioCreateParamsBase):
    stream: Required[Literal[True]]
    """
    If true, output is streamed for several characters at a time instead of waiting
    for the full response. The stream terminates with `data: [DONE]`. If false,
    return the encoded audio as octet stream
    """


AudioCreateParams = Union[AudioCreateParamsNonStreaming, AudioCreateParamsStreaming]
