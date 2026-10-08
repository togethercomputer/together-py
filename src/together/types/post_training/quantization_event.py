# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .quantization_results import QuantizationResults

__all__ = ["QuantizationEvent"]


class QuantizationEvent(BaseModel):
    """Event emitted by a quantization job."""

    created_at: datetime
    """Time when the event was created."""

    level: Literal["Info", "Warning", "Error"]
    """Event severity level."""

    message: str
    """Human-readable event message."""

    object: Literal["shaping"]
    """Object type, always `shaping`."""

    type: Literal[
        "SHAPING_ERROR",
        "SHAPING_USER_ERROR",
        "QUANTIZATION_JOB_START",
        "QUANTIZATION_MODEL_DOWNLOAD_COMPLETE",
        "QUANTIZATION_MERGE_COMPLETE",
        "QUANTIZATION_QUANTIZE_PROCESS_START",
        "QUANTIZATION_QUANTIZE_PROCESS_COMPLETE",
        "QUANTIZATION_MODEL_UPLOAD_COMPLETE",
        "QUANTIZATION_JOB_COMPLETE",
    ]
    """Quantization event type."""

    hash: Optional[str] = None
    """Event hash used for deduplication."""

    result: Optional[QuantizationResults] = None
    """Result attached to completion events."""
