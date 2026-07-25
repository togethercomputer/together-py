# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["SamplingParams"]


class SamplingParams(TypedDict, total=False):
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
