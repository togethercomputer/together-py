# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["OperationSampleParams", "ModelInput", "ModelInputChunk", "ModelInputChunkEncodedText", "SamplingParams"]


class OperationSampleParams(TypedDict, total=False):
    model_inputs: Required[Iterable[ModelInput]]
    """Model inputs to sample from"""

    num_samples: int
    """Number of completions to generate per prompt"""

    sampling_params: SamplingParams
    """Optional sampling parameters"""


class ModelInputChunkEncodedText(TypedDict, total=False):
    tokens: Required[SequenceNotStr[Union[str, int]]]
    """Pre-tokenized text input"""


class ModelInputChunk(TypedDict, total=False):
    encoded_text: ModelInputChunkEncodedText


class ModelInput(TypedDict, total=False):
    chunks: Required[Iterable[ModelInputChunk]]
    """Input chunks for the model"""


class SamplingParams(TypedDict, total=False):
    """Optional sampling parameters"""

    max_tokens: int
    """Maximum number of tokens to generate per completion"""

    return_prompt_logprobs: bool
    """
    When true, also return teacher-forced log-probabilities for the model input
    tokens in `SampleResult.prompt_logprobs`.
    """

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
