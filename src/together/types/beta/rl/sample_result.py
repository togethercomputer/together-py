# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .sampled_sequence import SampledSequence
from .policy_version_segment import PolicyVersionSegment

__all__ = ["SampleResult"]


class SampleResult(BaseModel):
    """Completions generated for a single model input"""

    policy_segments: List[PolicyVersionSegment]
    """Policy versions that produced these completions"""

    sequences: List[SampledSequence]
    """Generated completions"""

    prompt_logprobs: Optional[List[float]] = None
    """
    Teacher-forced log-probabilities for the model input tokens, one per token after
    the first (log P(token*i | token*<i)). Present only when return_prompt_logprobs
    was set on the request.
    """
