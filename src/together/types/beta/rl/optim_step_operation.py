# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .optim_step_result import OptimStepResult
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus

__all__ = ["OptimStepOperation"]


class OptimStepOperation(BaseModel):
    """Async optimizer step operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[OptimStepResult] = None
    """Result on success"""
