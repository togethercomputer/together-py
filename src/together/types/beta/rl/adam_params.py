# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["AdamParams"]


class AdamParams(TypedDict, total=False):
    """Per-step Adam optimizer overrides."""

    beta1: float
    """Exponential decay rate for the first-moment estimate"""

    beta2: float
    """Exponential decay rate for the second-moment estimate"""

    eps: float
    """Epsilon for numerical stability"""

    grad_clip_norm: float
    """
    Maximum gradient norm for this step, gradients across all model parameters are
    clipped to this value. Set to 0 to disable gradient clipping. When unset,
    gradients are clipped to the session default (1.0).
    """

    learning_rate: float
    """Learning rate for the Adam-tuned parameters"""

    weight_decay: float
    """Weight decay coefficient"""
