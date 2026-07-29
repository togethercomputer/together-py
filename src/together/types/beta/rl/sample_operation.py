# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel
from .sample_result import SampleResult
from .training_operation_error import TrainingOperationError
from .training_operation_status import TrainingOperationStatus

__all__ = ["SampleOperation", "Output"]


class Output(BaseModel):
    """Result on success"""

    results: List[SampleResult]
    """One result per model input"""


class SampleOperation(BaseModel):
    """Async sample operation"""

    id: str
    """Operation ID"""

    status: TrainingOperationStatus
    """Operation status"""

    error: Optional[TrainingOperationError] = None
    """Error details on failure"""

    output: Optional[Output] = None
    """Result on success"""
