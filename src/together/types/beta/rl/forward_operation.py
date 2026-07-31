# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .forward_result import ForwardResult
from .operation_error import OperationError
from .operation_status import OperationStatus

__all__ = ["ForwardOperation"]


class ForwardOperation(BaseModel):
    """Async forward pass operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[ForwardResult] = None
    """Result on success"""
