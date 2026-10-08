# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .volume_origin_param import VolumeOriginParam

__all__ = ["VolumeCreateParams", "Content"]


class VolumeCreateParams(TypedDict, total=False):
    content: Required[Content]
    """Content specifies the new content to preload to this volume."""

    name: Required[str]
    """Name is the unique identifier for the volume within the project"""

    type: Required[Literal["readOnly"]]
    """Type is the volume type (currently only "readOnly" is supported)"""


class Content(TypedDict, total=False):
    """Content specifies the new content to preload to this volume."""

    origin: VolumeOriginParam
    """
    External source Together copies into a new volume version; mutually exclusive
    with source_prefix.
    """

    source_prefix: str
    """
    SourcePrefix is the file path prefix for the content to be preloaded into the
    volume. Mutually exclusive with Origin
    """

    type: Literal["files"]
    """
    Type is the content type (currently only "files" is supported which allows
    preloading files uploaded via Files API into the volume)
    """
