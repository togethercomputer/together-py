# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .adamw_optimizer_params import AdamwOptimizerParams

__all__ = ["MuonOptimizerParams"]


class MuonOptimizerParams(TypedDict, total=False):
    """Per-step Muon optimizer overrides"""

    adamw: AdamwOptimizerParams
    """
    Per-step AdamW optimizer overrides for the AdamW-tuned parameters in a
    Muon-tuned optimizer session.
    """

    learning_rate: float
    """Learning rate for this Muon optimizer step."""

    momentum: float
    """Momentum coefficient"""

    newton_schulz_steps: int
    """Number of Newton-Schulz iterations"""

    weight_decay: float
    """Weight decay coefficient"""
