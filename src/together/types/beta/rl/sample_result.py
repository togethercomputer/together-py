# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ...._models import BaseModel
from .policy_version_segment import PolicyVersionSegment

__all__ = ["SampleResult", "Rollout", "RolloutSequence"]


class RolloutSequence(BaseModel):
    """A single generated completion sequence with tokens and logprobs"""

    tokens: List[Union[str, int]]
    """Generated token IDs"""

    logprobs: Optional[List[float]] = None
    """Log probabilities for each generated token"""

    stop_reason: Optional[str] = None
    """Reason for stopping generation"""


class Rollout(BaseModel):
    """Completions generated for a single prompt"""

    sequences: List[RolloutSequence]
    """Completions generated for one prompt"""

    prompt_logprobs: Optional[List[float]] = None
    """
    Teacher-forced log-probabilities for the prompt tokens, one per token after the
    first (log P(token*i | token*<i)). Present only when return_prompt_logprobs was
    set on the request.
    """


class SampleResult(BaseModel):
    """Result of a sample operation"""

    rollouts: List[Rollout]
    """Completions grouped by prompt"""

    policy_segments: Optional[List[PolicyVersionSegment]] = None
    """Policy versions that produced the returned rollouts.

    Most rollouts carry a single segment `(version, start_token=0)`; longer rollouts
    may carry multiple segments when the policy was updated mid-generation.
    """
