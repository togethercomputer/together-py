# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ...._models import BaseModel
from ...post_training.quantization_job import QuantizationJob

__all__ = ["PrepareForFp4InferenceListResponse"]


class PrepareForFp4InferenceListResponse(BaseModel):
    """List response containing shaping jobs."""

    data: List[QuantizationJob]
    """Shaping jobs."""

    object: Literal["list"]
    """Object type, always `list`."""
