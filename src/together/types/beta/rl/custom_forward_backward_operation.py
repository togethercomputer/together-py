# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .operation_error import OperationError
from .operation_status import OperationStatus
from .custom_forward_backward_result import CustomForwardBackwardResult

__all__ = ["CustomForwardBackwardOperation"]


class CustomForwardBackwardOperation(BaseModel):
    """Async custom forward-backward pass operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[CustomForwardBackwardResult] = None
    """Result on success"""
