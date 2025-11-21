# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SpeechCreateParamsBase", "SpeechCreateParamsNonStreaming", "SpeechCreateParamsStreaming"]


class SpeechCreateParamsBase(TypedDict, total=False):
    input: Required[str]
    """Input text to generate the audio for"""

    model: Required[Union[Literal["cartesia/sonic", "hexgrad/Kokoro-82M", "canopylabs/orpheus-3b-0.1-ft"], str]]
    """The name of the model to query.

    [See all of Together AI's chat models](https://docs.together.ai/docs/serverless-models#audio-models)
    The current supported tts models are: - cartesia/sonic - hexgrad/Kokoro-82M -
    canopylabs/orpheus-3b-0.1-ft
    """

    voice: Required[str]
    """The voice to use for generating the audio.

    The voices supported are different for each model. For eg - for
    canopylabs/orpheus-3b-0.1-ft, one of the voices supported is tara, for
    hexgrad/Kokoro-82M, one of the voices supported is af_alloy and for
    cartesia/sonic, one of the voices supported is "friendly sidekick".

    You can view the voices supported for each model using the /v1/voices endpoint
    sending the model name as the query parameter.
    [View all supported voices here](https://docs.together.ai/docs/text-to-speech#voices-available).
    """

    language: Literal["en", "de", "fr", "es", "hi", "it", "ja", "ko", "nl", "pl", "pt", "ru", "sv", "tr", "zh"]
    """Language of input text."""

    response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"]
    """Audio encoding of response"""

    response_format: Literal["mp3", "wav", "raw"]
    """The format of audio output.

    Supported formats are mp3, wav, raw if streaming is false. If streaming is true,
    the only supported format is raw.
    """

    sample_rate: int
    """Sampling rate to use for the output audio.

    The default sampling rate for canopylabs/orpheus-3b-0.1-ft and
    hexgrad/Kokoro-82M is 24000 and for cartesia/sonic is 44100.
    """


class SpeechCreateParamsNonStreaming(SpeechCreateParamsBase, total=False):
    stream: Literal[False]
    """
    If true, output is streamed for several characters at a time instead of waiting
    for the full response. The stream terminates with `data: [DONE]`. If false,
    return the encoded audio as octet stream
    """


class SpeechCreateParamsStreaming(SpeechCreateParamsBase):
    stream: Required[Literal[True]]
    """
    If true, output is streamed for several characters at a time instead of waiting
    for the full response. The stream terminates with `data: [DONE]`. If false,
    return the encoded audio as octet stream
    """


SpeechCreateParams = Union[SpeechCreateParamsNonStreaming, SpeechCreateParamsStreaming]
