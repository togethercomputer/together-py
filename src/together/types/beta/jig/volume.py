# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from .volume_origin import VolumeOrigin
from .volume_status import VolumeStatus

__all__ = ["Volume", "Content", "ContentFile", "VersionHistory", "VersionHistoryContent"]


class ContentFile(BaseModel):
    last_modified: Optional[str] = None
    """LastModified is the timestamp when the file was last modified"""

    name: Optional[str] = None
    """Name is the filename including extension (e.g., "model_weights.bin")"""

    size: Optional[int] = None
    """Size is the file size in bytes"""


class Content(BaseModel):
    """Content currently available on a volume version."""

    files: Optional[List[ContentFile]] = None
    """
    Files is the list of files to preload into the volume, if the volume content
    type is "files".
    """

    origin: Optional[VolumeOrigin] = None
    """External source Together copied into this volume version."""

    source_prefix: Optional[str] = None
    """
    SourcePrefix is the file path prefix for the content to be preloaded into the
    volume
    """

    type: Optional[Literal["files"]] = None
    """
    Type is the content type (currently only "files" is supported which allows
    preloading files uploaded via Files API into the volume)
    """


class VersionHistoryContent(BaseModel):
    """Content configuration used to create this version."""

    origin: Optional[VolumeOrigin] = None
    """
    External source Together copies into a new volume version; mutually exclusive
    with source_prefix.
    """

    source_prefix: Optional[str] = None
    """
    SourcePrefix is the file path prefix for the content to be preloaded into the
    volume. Mutually exclusive with Origin
    """

    type: Optional[Literal["files"]] = None
    """
    Type is the content type (currently only "files" is supported which allows
    preloading files uploaded via Files API into the volume)
    """


class VersionHistory(BaseModel):
    """Metadata for a previous volume version."""

    content: Optional[VersionHistoryContent] = None
    """Content configuration used to create this version."""

    mounted_by: Optional[List[str]] = None
    """Deployment IDs currently mounting this version."""

    status: Optional[VolumeStatus] = None
    """Status of this volume version."""

    status_message: Optional[str] = None
    """Message explaining why this volume version failed, when applicable."""

    version: Optional[int] = None
    """Numeric version identifier for this volume content."""


class Volume(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier for this volume"""

    content: Optional[Content] = None
    """Content currently available on a volume version."""

    created_at: Optional[str] = None
    """CreatedAt is the ISO8601 timestamp when this volume was created"""

    current_version: Optional[int] = None
    """CurrentVersion is the current version number of this volume"""

    mounted_by: Optional[List[str]] = None
    """
    MountedBy is the list of deployment IDs currently mounting current volume
    version
    """

    name: Optional[str] = None
    """Name is the name of the volume"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "volume")"""

    status: Optional[VolumeStatus] = None
    """Status of the current volume version."""

    status_message: Optional[str] = None
    """Message explaining why the current volume version failed, when applicable."""

    type: Optional[Literal["readOnly"]] = None

    updated_at: Optional[str] = None
    """UpdatedAt is the ISO8601 timestamp when this volume was last updated"""

    version_history: Optional[Dict[str, VersionHistory]] = None
    """
    VersionHistory contains previous versions of this volume, keyed by version
    number
    """
