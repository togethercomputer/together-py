# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["CosineLrSchedulerArgs"]


class CosineLrSchedulerArgs(BaseModel):
    min_lr_ratio: float
    """The ratio of the final learning rate to the peak learning rate"""

    num_cycles: float
    """Number or fraction of cycles for the cosine learning rate scheduler"""
