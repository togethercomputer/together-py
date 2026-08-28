# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["PolicyVersionSegment"]


class PolicyVersionSegment(BaseModel):
    """A (policy version, starting token) span within a sampled sequence.

    Version 0 is the initial model; each optim_step call increments the version by 1.
    """

    start_token: int
    """Index of the first token of this segment within the sampled sequence.

    Always 0 for the first segment.
    """

    version: int
    """Model version under which this segment of tokens was generated"""
