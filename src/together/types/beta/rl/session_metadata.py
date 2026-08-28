# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .wandb_metadata import WandbMetadata

__all__ = ["SessionMetadata"]


class SessionMetadata(BaseModel):
    """Auxiliary metadata associated with a training session"""

    wandb: Optional[WandbMetadata] = None
    """Weights & Biases details associated with the training session"""
