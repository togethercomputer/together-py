# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .cosine_lr_scheduler_args import CosineLrSchedulerArgs
from .linear_lr_scheduler_args import LinearLrSchedulerArgs

__all__ = ["LrScheduler", "LrSchedulerArgs"]

LrSchedulerArgs: TypeAlias = Union[LinearLrSchedulerArgs, CosineLrSchedulerArgs]


class LrScheduler(BaseModel):
    lr_scheduler_type: Literal["linear", "cosine"]

    lr_scheduler_args: Optional[LrSchedulerArgs] = None
