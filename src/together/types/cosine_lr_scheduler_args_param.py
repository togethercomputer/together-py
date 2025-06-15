# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CosineLrSchedulerArgsParam"]


class CosineLrSchedulerArgsParam(TypedDict, total=False):
    min_lr_ratio: Required[float]
    """The ratio of the final learning rate to the peak learning rate"""

    num_cycles: Required[float]
    """Number or fraction of cycles for the cosine learning rate scheduler"""
