# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .operation_error import OperationError
from .operation_status import OperationStatus
from .optim_step_result import OptimStepResult

__all__ = ["OptimStepOperation"]


class OptimStepOperation(BaseModel):
    """Async optimizer step operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[OptimStepResult] = None
    """Result on success"""
