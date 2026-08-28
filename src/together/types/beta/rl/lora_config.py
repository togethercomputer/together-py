# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional

from ...._models import BaseModel

__all__ = ["LoraConfig"]


class LoraConfig(BaseModel):
    """LoRA adapter configuration"""

    alpha: Optional[int] = None
    """Alpha of the LoRA adapter"""

    dropout: Optional[float] = None
    """Dropout of the LoRA adapter"""

    rank: Optional[int] = None
    """Rank of the LoRA adapter"""

    seed: Union[str, int, None] = None
    """Random seed for initializing LoRA adapter weights.

    Ignored when LoRA is disabled or the session resumes from a checkpoint.
    """

    train_unembed: Optional[bool] = None
    """Whether to also train a LoRA adapter on the output head. Defaults to true."""
