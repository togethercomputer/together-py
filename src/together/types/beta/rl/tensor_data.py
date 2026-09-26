# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["TensorData"]


class TensorData(BaseModel):
    """A tensor encoded as flattened row-major values, with an optional shape."""

    data: List[float]
    """Flattened one-dimensional values encoded as JSON numbers."""

    dtype: Literal["int64", "float32"]
    """Tensor element type, either `int64` or `float32`."""

    shape: Optional[List[int]] = None
    """
    Optional tensor shape; training operations accept one-dimensional tensors only,
    and the dimension must match the data length.
    """

    sparse_col_indices: Optional[List[int]] = None
    """Unsupported for training operations. Omit this field."""

    sparse_crow_indices: Optional[List[int]] = None
    """Unsupported for training operations. Omit this field."""
