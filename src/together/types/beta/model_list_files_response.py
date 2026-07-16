# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ModelListFilesResponse", "Data"]


class Data(BaseModel):
    """Metadata for one file in a model revision."""

    hash: Optional[str] = None
    """Content hash for integrity verification and upload deduplication."""

    path: Optional[str] = None
    """File path within the model revision."""

    size_bytes: Optional[str] = FieldInfo(alias="sizeBytes", default=None)
    """File size in bytes."""


class ModelListFilesResponse(BaseModel):
    """Files and aggregate size information for one model revision."""

    data: List[Data]
    """Files in the selected model revision."""

    object: Literal["list"]

    next_cursor: Optional[str] = None
    """Cursor for the next page. Null if there are no more results."""

    revision_created_at: Optional[datetime] = FieldInfo(alias="revisionCreatedAt", default=None)
    """Time when the listed model revision was created."""

    revision_id: Optional[str] = FieldInfo(alias="revisionId", default=None)
    """ID of the model revision whose files are listed."""

    total_size_bytes: Optional[str] = FieldInfo(alias="totalSizeBytes", default=None)
    """Total size of all files in the revision, in bytes."""
