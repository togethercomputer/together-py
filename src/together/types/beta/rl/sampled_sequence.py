# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional

from ...._models import BaseModel
from .stop_reason import StopReason
from .routed_experts import RoutedExperts

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

    routed_experts: Optional[RoutedExperts] = None
    """
    MoE per-token routing decisions captured during generation; absent for dense
    models or when capture is disabled.
    """
