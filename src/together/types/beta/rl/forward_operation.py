# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .forward_result import ForwardResult
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus

__all__ = ["ForwardOperation"]


class ForwardOperation(BaseModel):
    """Async forward pass operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[ForwardResult] = None
    """Result on success"""
