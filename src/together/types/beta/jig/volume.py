# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Volume", "Content"]


class Content(BaseModel):
    """Content specifies the content that will be preloaded to this volume"""

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


class Volume(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier for this volume"""

    content: Optional[Content] = None
    """Content specifies the content that will be preloaded to this volume"""

    created_at: Optional[str] = None
    """CreatedAt is the ISO8601 timestamp when this volume was created"""

    name: Optional[str] = None
    """Name is the name of the volume"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "volume")"""

    type: Optional[Literal["readOnly"]] = None
    """Type is the volume type (e.g., "readOnly")"""

    updated_at: Optional[str] = None
    """UpdatedAt is the ISO8601 timestamp when this volume was last updated"""
