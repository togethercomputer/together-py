# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr

__all__ = ["LossTargetTokensParam"]


class LossTargetTokensParam(TypedDict, total=False):
    data: Required[SequenceNotStr[Union[str, int]]]
    """Integer array of target tokens"""

    dtype: DType
    """Data type of the integer array"""
