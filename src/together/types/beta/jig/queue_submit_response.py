# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["QueueSubmitResponse", "Error"]


class Error(BaseModel):
    code: Optional[str] = None

    message: Optional[str] = None

    param: Optional[str] = None

    type: Optional[str] = None


class QueueSubmitResponse(BaseModel):
    error: Optional[Error] = None

    request_id: Optional[str] = FieldInfo(alias="requestId", default=None)
