# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["OperationSampleParams", "Prompt", "PromptChunk", "PromptChunkEncodedText", "SamplingParams"]


class OperationSampleParams(TypedDict, total=False):
    prompts: Required[Iterable[Prompt]]
    """Input prompts as tokenized chunks"""

    num_samples: int
    """Number of completions to generate per prompt"""

    sampling_params: SamplingParams
    """Optional sampling parameters"""


class PromptChunkEncodedText(TypedDict, total=False):
    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""


class PromptChunk(TypedDict, total=False):
    encoded_text: PromptChunkEncodedText


class Prompt(TypedDict, total=False):
    chunks: Required[Iterable[PromptChunk]]
    """Input chunks for the model"""


class SamplingParams(TypedDict, total=False):
    """Optional sampling parameters"""

    max_tokens: int
    """Maximum number of tokens to generate per completion"""

    seed: Union[str, int]
    """Random seed for reproducibility"""

    stop: SequenceNotStr[str]
    """Generation stops when any of these strings is produced"""

    temperature: float
    """Sampling temperature"""

    top_k: int
    """Top-k sampling limit"""

    top_p: float
    """Nucleus sampling probability threshold"""
