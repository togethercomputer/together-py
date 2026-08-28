# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ...._models import BaseModel
from .operation_error_code import OperationErrorCode

__all__ = ["OperationError"]


class OperationError(BaseModel):
    """Error details for a failed training operation"""

    code: Optional[OperationErrorCode] = None
    """Application error code"""

    message: Optional[str] = None
    """Human-readable error message"""
