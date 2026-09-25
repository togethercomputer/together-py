# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from ...._models import BaseModel
from .model_resources_error_code import ModelResourcesErrorCode

__all__ = ["ModelResourcesError"]


class ModelResourcesError(BaseModel):
    """Structured detail for the model resource's current error"""

    code: ModelResourcesErrorCode
    """Finite machine-readable reason code for UI branching"""

    message: str
    """User-safe human-readable detail for the current status"""

    occurred_at: datetime
    """Timestamp when this error was reported"""
