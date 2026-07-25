# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ...._models import BaseModel
from .stop_reason import StopReason
from .policy_version_segment import PolicyVersionSegment

__all__ = ["SampleResult", "Sequence"]


class Sequence(BaseModel):
    """A single generated completion sequence with tokens and logprobs"""

    stop_reason: StopReason
    """Reason for stopping generation"""

    tokens: List[Union[str, int]]
    """Generated token IDs"""

    logprobs: Optional[List[float]] = None
    """Log probabilities for each generated token"""


class SampleResult(BaseModel):
    """Completions generated for a single model input"""

    policy_segments: List[PolicyVersionSegment]
    """Policy versions that produced these completions"""

    sequences: List[Sequence]
    """Generated completions"""

    prompt_logprobs: Optional[List[float]] = None
    """
    Teacher-forced log-probabilities for the model input tokens, one per token after
    the first (log P(token*i | token*<i)). Present only when return_prompt_logprobs
    was set on the request.
    """
