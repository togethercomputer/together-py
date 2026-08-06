# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .d_type import DType

__all__ = ["Weights"]


class Weights(TypedDict, total=False):
    data: Required[Iterable[float]]
    """Per-token loss weights, one non-negative weight per target token.

    A weight of 0 excludes the token from loss; fractional weights are honored only
    by cross-entropy.
    """

    dtype: DType
    """Data type of the weights array (must be D_TYPE_FLOAT32)."""
