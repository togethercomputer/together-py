# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .adam_params import AdamParams

__all__ = ["MuonParams"]


class MuonParams(TypedDict, total=False):
    """Per-step Muon optimizer overrides"""

    adam: AdamParams
    """
    Per-step Adam optimizer overrides for the Adam-tuned parameters in a Muon-tuned
    optimizer session.
    """

    grad_clip_norm: float
    """
    Maximum gradient norm for this step, gradients across all model parameters are
    clipped to this value. Set to 0 to disable gradient clipping. When unset,
    gradients are clipped to the session default (1.0).
    """

    learning_rate: float
    """Learning rate for this Muon optimizer step."""

    momentum: float
    """Momentum coefficient"""

    newton_schulz_steps: int
    """Number of Newton-Schulz iterations"""

    weight_decay: float
    """Weight decay coefficient"""
