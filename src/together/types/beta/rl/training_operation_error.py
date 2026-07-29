# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .training_operation_error_code import TrainingOperationErrorCode

__all__ = ["TrainingOperationError"]


class TrainingOperationError(BaseModel):
    """Error details for a failed training operation"""

    code: Optional[TrainingOperationErrorCode] = None
    """Application error code"""

    message: Optional[str] = None
    """Human-readable error message"""
