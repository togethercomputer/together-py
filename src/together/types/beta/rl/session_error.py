# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ...._models import BaseModel
from .session_error_code import SessionErrorCode

__all__ = ["SessionError"]


class SessionError(BaseModel):
    """Structured detail for the training session's current error"""

    code: SessionErrorCode
    """Finite machine-readable reason code for UI branching"""

    message: str
    """User-safe human-readable detail for the current status"""

    occurred_at: datetime
    """Timestamp when this error was reported"""
