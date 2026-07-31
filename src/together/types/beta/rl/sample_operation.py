# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .sample_result import SampleResult
from .operation_error import OperationError
from .operation_status import OperationStatus

__all__ = ["SampleOperation", "Output"]


class Output(BaseModel):
    """Result on success"""

    results: List[SampleResult]
    """One result per model input"""


class SampleOperation(BaseModel):
    """Async sample operation"""

    id: str
    """Operation ID"""

    status: OperationStatus
    """Operation status"""

    error: Optional[OperationError] = None
    """Error details on failure"""

    output: Optional[Output] = None
    """Result on success"""
