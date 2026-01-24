# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["VolumeUpdateParams", "Content"]


class VolumeUpdateParams(TypedDict, total=False):
    content: Content
    """Content specifies the new content that will be preloaded to this volume"""

    name: str
    """Name is the new unique identifier for the volume within the project"""

    type: Literal["readOnly"]
    """Type is the new volume type (currently only "readOnly" is supported)"""


class Content(TypedDict, total=False):
    """Content specifies the new content that will be preloaded to this volume"""

    source_prefix: str
    """
    SourcePrefix is the file path prefix for the content to be preloaded into the
    volume
    """

    type: Literal["files"]
    """
    Type is the content type (currently only "files" is supported which allows
    preloading files uploaded via Files API into the volume)
    """
