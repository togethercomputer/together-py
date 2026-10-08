# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["TensorDataParam"]


class TensorDataParam(TypedDict, total=False):
    """A tensor encoded as flattened row-major values, with an optional shape."""

    data: Required[Iterable[float]]
    """Flattened one-dimensional values encoded as JSON numbers."""

    dtype: Required[Literal["int64", "float32"]]
    """Tensor element type, either `int64` or `float32`."""

    shape: Iterable[int]
    """
    Optional tensor shape; training operations accept one-dimensional tensors only,
    and the dimension must match the data length.
    """

    sparse_col_indices: Iterable[int]
    """Unsupported for training operations. Omit this field."""

    sparse_crow_indices: Iterable[int]
    """Unsupported for training operations. Omit this field."""
