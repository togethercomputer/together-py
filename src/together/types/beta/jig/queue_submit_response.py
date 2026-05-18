# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["QueueSubmitResponse"]


class QueueSubmitResponse(BaseModel):
    """Response returned after queueing a job."""

    request_id: str = FieldInfo(alias="requestId")
    """Unique identifier for the submitted job. Use this to poll status or cancel."""
