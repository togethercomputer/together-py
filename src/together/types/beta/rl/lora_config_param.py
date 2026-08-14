# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypedDict

__all__ = ["LoraConfigParam"]


class LoraConfigParam(TypedDict, total=False):
    """LoRA adapter configuration"""

    alpha: int
    """Alpha of the LoRA adapter"""

    dropout: float
    """Dropout of the LoRA adapter"""

    rank: int
    """Rank of the LoRA adapter"""

    seed: Union[str, int]
    """Random seed for initializing LoRA adapter weights.

    Ignored when LoRA is disabled or the session resumes from a checkpoint.
    """

    train_unembed: bool
    """Whether to also train a LoRA adapter on the output head. Defaults to true."""
