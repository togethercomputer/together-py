# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RemoteUploadEventsResponse", "Data"]


class Data(BaseModel):
    """Progress or diagnostic event emitted while importing remote model files."""

    id: str
    """Unique event identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Time when the event was recorded."""

    level: Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"]
    """Severity of the event."""

    message: str
    """Human-readable progress or diagnostic message."""

    type: str
    """Stable event type emitted by the importer, such as `download.started`."""


class RemoteUploadEventsResponse(BaseModel):
    """Status and diagnostic events for a remote model import job."""

    data: List[Data]
    """Events for the remote upload."""

    object: Literal["list"]
    """Object type. Always `list`."""

    next_cursor: Optional[str] = None
    """Cursor for the next page. Null if there are no more results."""
