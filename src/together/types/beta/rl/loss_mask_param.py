# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr

__all__ = ["LossMaskParam"]


class LossMaskParam(TypedDict, total=False):
    """Per-token loss mask (1=compute loss, 0=ignore)"""

    data: Required[SequenceNotStr[Union[str, int]]]
    """Integer array of per-token mask values (0s and 1s)"""

    dtype: DType
    """Data type of the integer array (must be D_TYPE_INT64)"""
