# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["SpeechCreateParamsBase", "ExtraParams", "SpeechCreateParamsNonStreaming", "SpeechCreateParamsStreaming"]


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
    [View all supported voices here](https://docs.together.ai/docs/text-to-speech#supported-voices).

    `hexgrad/Kokoro-82M` additionally supports voice mixing, where two or more
    voices are combined into a single blended voice by joining their names with `+`
    (e.g. `af_bella+af_heart`). Optional per-voice weights can be provided in
    parentheses (e.g. `af_bella(2)+af_heart(1)`). Other models require a single
    voice name.
    """

    bit_rate: Literal[32000, 64000, 96000, 128000, 192000]
    """Bitrate of the MP3 audio output in bits per second.

    Only applicable when response_format is mp3. Higher values produce better audio
    quality at larger file sizes. Default is 128000. Currently supported on Cartesia
    models.
    """

    extra_params: ExtraParams
    """Additional model-specific parameters that fine-tune speech generation behavior."""

    language: str
    """Language or locale of input text.

    Accepts ISO 639-1 language codes (e.g., `en`, `fr`, `es`, `zh`) as well as
    locale codes for region-specific variants. Locale codes must be lowercase (e.g.,
    `zh-hk` for Cantonese).
    """

    response_encoding: Literal["pcm_f32le", "pcm_s16le", "pcm_mulaw", "pcm_alaw"]
    """Audio encoding of response.

    Only applicable when response_format is raw or pcm. Cartesia models respect this
    parameter and support all values. Orpheus, Kokoro, and Minimax models always
    return pcm_s16le regardless of this setting.
    """

    response_format: Literal["mp3", "wav", "raw"]
    """The format of audio output.

    Supported formats are mp3, wav, raw if streaming is false. If streaming is true,
    the only supported format is raw.
    """

    sample_rate: int
    """Sampling rate in Hz for the output audio.

    Cartesia and Minimax models respect this parameter. Orpheus and Kokoro models
    always output at 24000 Hz regardless of this setting.
    """


class ExtraParams(TypedDict, total=False):
    """Additional model-specific parameters that fine-tune speech generation behavior."""

    pronunciation_dict: SequenceNotStr[str]
    """A list of pronunciation rules for specific characters or symbols.

    Each entry uses the format `"<source>/<replacement>"` (e.g.,
    `["omg/oh my god"]`) to override how the model pronounces matching tokens.
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
