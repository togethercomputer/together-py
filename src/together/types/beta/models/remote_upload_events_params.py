# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RemoteUploadEventsParams"]


class RemoteUploadEventsParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous remote upload event list response."""

    limit: int
    """Maximum number of events to return."""
