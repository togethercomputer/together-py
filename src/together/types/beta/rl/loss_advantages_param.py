# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType

__all__ = ["LossAdvantages"]


class LossAdvantages(TypedDict, total=False):
    data: Required[Iterable[float]]
    """Float array of per-token advantages"""

    dtype: DType
    """Data type of the float array (D_TYPE_FLOAT32 or D_TYPE_BFLOAT16)"""
