# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus
from .inference_checkpoint_result import InferenceCheckpointResult

__all__ = ["InferenceCheckpointOperation"]


class InferenceCheckpointOperation(BaseModel):
    """Async inference checkpoint operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[InferenceCheckpointResult] = None
    """Result on success"""
