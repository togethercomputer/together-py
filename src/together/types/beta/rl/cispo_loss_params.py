# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CispoLossParams"]


class CispoLossParams(TypedDict, total=False):
    clip_high_threshold: float
    """
    Upper absolute bound for the importance ratio; the clipped ratio is applied as a
    detached coefficient
    """

    clip_low_threshold: float
    """
    Lower absolute bound for the importance ratio; the clipped ratio is applied as a
    detached coefficient
    """
