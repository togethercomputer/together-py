# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypedDict

from .d_type import DType
from ...._types import SequenceNotStr

__all__ = ["Weights"]


class Weights(TypedDict, total=False):
    data: Required[SequenceNotStr[Union[str, int]]]
    """Per-token weights: 1 to include the token in the loss, 0 to ignore it."""

    dtype: DType
    """Data type of the integer array (must be D_TYPE_INT64)"""
