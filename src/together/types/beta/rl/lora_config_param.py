# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["LoraConfigParam"]


class LoraConfigParam(TypedDict, total=False):
    """LoRA adapter configuration"""

    alpha: int
    """Alpha of the LoRA adapter"""

    dropout: float
    """Dropout of the LoRA adapter"""

    enable: bool
    """Whether to enable LoRA fine-tuning. If false, full fine-tuning is used."""

    rank: int
    """Rank of the LoRA adapter"""
