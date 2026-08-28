# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .operation_error import OperationError
from .operation_status import OperationStatus
from .inference_checkpoint_result import InferenceCheckpointResult

__all__ = ["InferenceCheckpointOperation"]


class InferenceCheckpointOperation(BaseModel):
    """Async inference checkpoint operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[InferenceCheckpointResult] = None
    """Result on success"""
