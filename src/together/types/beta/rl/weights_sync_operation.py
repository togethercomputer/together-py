# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .operation_error import OperationError
from .operation_status import OperationStatus
from .weights_sync_result import WeightsSyncResult

__all__ = ["WeightsSyncOperation"]


class WeightsSyncOperation(BaseModel):
    """Async weights-sync operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[WeightsSyncResult] = None
    """Result on success"""
