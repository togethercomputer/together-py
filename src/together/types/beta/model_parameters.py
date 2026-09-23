# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .model_dtype_count import ModelDtypeCount

__all__ = ["ModelParameters"]


class ModelParameters(BaseModel):
    """Model parameter count and precision breakdown."""

    by_dtype: List[ModelDtypeCount] = FieldInfo(alias="byDtype")
    """Parameter counts grouped by numerical data type."""

    total: str
    """Total number of parameters in the model weights."""
