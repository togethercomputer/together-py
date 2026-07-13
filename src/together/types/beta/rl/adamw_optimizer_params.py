# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["AdamwOptimizerParams"]


class AdamwOptimizerParams(TypedDict, total=False):
    """Per-step AdamW optimizer overrides."""

    beta1: float
    """Exponential decay rate for the first-moment estimate"""

    beta2: float
    """Exponential decay rate for the second-moment estimate"""

    eps: float
    """Epsilon for numerical stability"""

    learning_rate: float
    """Learning rate for the AdamW-tuned parameters"""

    weight_decay: float
    """Weight decay coefficient"""
