# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["QueueSubmitResponse", "Error"]


class Error(BaseModel):
    code: Optional[str] = None
    """Machine-readable error code"""

    message: Optional[str] = None
    """Human-readable error message"""

    param: Optional[str] = None
    """The parameter that caused the error, if applicable"""

    type: Optional[str] = None
    """Error category (e.g. "invalid_request_error", "not_found_error")"""


class QueueSubmitResponse(BaseModel):
    error: Optional[Error] = None

    request_id: Optional[str] = FieldInfo(alias="requestId", default=None)
    """Unique identifier for the submitted job. Use this to poll status or cancel."""
