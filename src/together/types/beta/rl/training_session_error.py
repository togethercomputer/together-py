# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ...._models import BaseModel
from .training_session_error_code import TrainingSessionErrorCode

__all__ = ["TrainingSessionError"]


class TrainingSessionError(BaseModel):
    """Structured detail for the training session's current error"""

    code: TrainingSessionErrorCode
    """Finite machine-readable reason code for UI branching"""

    message: str
    """User-safe human-readable detail for the current status"""

    occurred_at: datetime
    """Timestamp when this error was reported"""
