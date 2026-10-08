# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DppoLossParams"]


class DppoLossParams(TypedDict, total=False):
    """Parameters for DPPO loss.

    Both probability-change limits must be in [0, 1] and default to 0.15.
    """

    delta_high: float
    """Probability-change limit for tokens with positive advantage.

    Measured in probability space, not log-probability space. Must be in [0, 1].
    Defaults to 0.15.
    """

    delta_low: float
    """Probability-change limit for tokens with negative advantage.

    Measured in probability space, not log-probability space. Must be in [0, 1].
    Defaults to 0.15.
    """
