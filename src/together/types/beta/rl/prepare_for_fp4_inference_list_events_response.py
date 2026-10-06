# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ...._models import BaseModel
from .quantization_event import QuantizationEvent

__all__ = ["PrepareForFp4InferenceListEventsResponse"]


class PrepareForFp4InferenceListEventsResponse(BaseModel):
    """List response containing shaping events."""

    data: List[QuantizationEvent]
    """Shaping events."""

    object: Literal["list"]
    """Object type, always `list`."""
