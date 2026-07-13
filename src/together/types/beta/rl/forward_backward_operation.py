# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .forward_backward_result import ForwardBackwardResult
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus

__all__ = ["ForwardBackwardOperation"]


class ForwardBackwardOperation(BaseModel):
    """Async forward-backward pass operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[ForwardBackwardResult] = None
    """Result on success"""
