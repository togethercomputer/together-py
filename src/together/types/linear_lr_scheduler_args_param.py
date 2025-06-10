# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["LinearLrSchedulerArgsParam"]


class LinearLrSchedulerArgsParam(TypedDict, total=False):
    min_lr_ratio: float
    """The ratio of the final learning rate to the peak learning rate"""
