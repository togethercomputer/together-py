# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["LogProbs", "Content"]


class Content(BaseModel):
    token: str

    logprob: float


class LogProbs(BaseModel):
    content: Optional[List[Content]] = None

    token_logprobs: Optional[List[float]] = None
    """List of token log probabilities"""

    tokens: Optional[List[str]] = None
    """List of token strings"""
