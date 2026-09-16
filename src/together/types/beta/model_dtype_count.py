# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["ModelDtypeCount"]


class ModelDtypeCount(BaseModel):
    """Number of model parameters stored in one numerical data type."""

    count: str
    """Number of model parameters stored with this data type."""

    dtype: str
    """Numerical data type, such as `float16`, `bfloat16`, or `int8`."""
