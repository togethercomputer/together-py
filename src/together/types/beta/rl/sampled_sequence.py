# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ...._models import BaseModel
from .stop_reason import StopReason

__all__ = ["SampledSequence"]


class SampledSequence(BaseModel):
    """A single generated completion sequence with tokens and logprobs"""

    prompt_cache_hit_tokens: int
    """
    Number of model input tokens served from the prefix cache while generating this
    sequence.
    """

    stop_reason: StopReason
    """Reason for stopping generation"""

    tokens: List[Union[str, int]]
    """Generated token IDs"""

    logprobs: Optional[List[float]] = None
    """Log probabilities for each generated token"""
