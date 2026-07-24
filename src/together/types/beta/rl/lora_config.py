# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel

__all__ = ["LoraConfig"]


class LoraConfig(BaseModel):
    """LoRA adapter configuration"""

    alpha: Optional[int] = None
    """Alpha of the LoRA adapter"""

    dropout: Optional[float] = None
    """Dropout of the LoRA adapter"""

    enable: Optional[bool] = None
    """Whether to enable LoRA fine-tuning. If false, full fine-tuning is used."""

    rank: Optional[int] = None
    """Rank of the LoRA adapter"""
