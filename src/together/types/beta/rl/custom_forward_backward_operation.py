# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus

__all__ = ["CustomForwardBackwardOperation"]


class CustomForwardBackwardOperation(BaseModel):
    """Async custom forward-backward pass operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[object] = None
    """Result on success"""
