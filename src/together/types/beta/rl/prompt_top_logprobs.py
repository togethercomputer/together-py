# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["PromptTopLogprobs"]


class PromptTopLogprobs(BaseModel):
    """
    The most likely alternative tokens at a single prompt position, as two parallel arrays of equal length. Both are empty for a position with no conditioning context, such as position 0.
    """

    logprobs: Optional[List[float]] = None
    """Log-probability of each alternative in `token_ids`, at the same index."""

    token_ids: Optional[List[int]] = None
    """Token IDs of the alternatives, ordered by descending log-probability."""
