# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["QuantizationResults"]


class QuantizationResults(BaseModel):
    """Model artifact produced by a completed quantization job."""

    api_model_object_id: Optional[str] = FieldInfo(alias="model_object_id", default=None)
    """Model object ID registered by the job."""

    api_model_revision_id: Optional[str] = FieldInfo(alias="model_revision_id", default=None)
    """Model revision ID registered by the job."""
