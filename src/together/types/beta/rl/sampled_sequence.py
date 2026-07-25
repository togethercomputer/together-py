# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union

from ...._models import BaseModel
from .stop_reason import StopReason

__all__ = ["SampledSequence"]


class SampledSequence(BaseModel):
    """A single generated completion sequence with tokens and logprobs"""

    logprobs: List[float]
    """Log probabilities for each generated token"""

    stop_reason: StopReason
    """Reason for stopping generation"""

    tokens: List[Union[str, int]]
    """Generated token IDs"""
