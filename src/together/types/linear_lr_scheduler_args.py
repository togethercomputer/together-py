# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["LinearLrSchedulerArgs"]


class LinearLrSchedulerArgs(BaseModel):
    min_lr_ratio: Optional[float] = None
    """The ratio of the final learning rate to the peak learning rate"""
