# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel

__all__ = ["ForwardResult", "Logprob"]


class Logprob(BaseModel):
    """Per-token log-probabilities from the target model"""

    data: List[float]
    """Float array of per-token log probabilities"""


class ForwardResult(BaseModel):
    """Result of a forward pass operation"""

    logprobs: List[Logprob]
    """Per-sample per-token log-probabilities"""
