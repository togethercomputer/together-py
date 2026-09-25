# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .muon_scaling_strategy import MuonScalingStrategy

__all__ = ["MuonConfigParam"]


class MuonConfigParam(TypedDict, total=False):
    """Advanced configuration for the Muon optimizer."""

    scaling_strategy: MuonScalingStrategy
    """Scaling strategy for the Muon optimizer."""
