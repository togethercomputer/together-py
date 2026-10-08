# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CispoLossParams"]


class CispoLossParams(TypedDict, total=False):
    clip_high_threshold: float
    """Upper bound for clipping the importance-sampling ratio."""

    clip_low_threshold: float
    """Lower bound for clipping the importance-sampling ratio."""
