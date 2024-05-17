# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["LogProbs"]


class LogProbs(BaseModel):
    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""
