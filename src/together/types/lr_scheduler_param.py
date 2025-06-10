# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .cosine_lr_scheduler_args_param import CosineLrSchedulerArgsParam
from .linear_lr_scheduler_args_param import LinearLrSchedulerArgsParam

__all__ = ["LrSchedulerParam", "LrSchedulerArgs"]

LrSchedulerArgs: TypeAlias = Union[LinearLrSchedulerArgsParam, CosineLrSchedulerArgsParam]


class LrSchedulerParam(TypedDict, total=False):
    lr_scheduler_type: Required[Literal["linear", "cosine"]]

    lr_scheduler_args: LrSchedulerArgs
