# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["VolumeCreateParams", "Content"]


class VolumeCreateParams(TypedDict, total=False):
    content: Required[Content]
    """Content specifies the content configuration for this volume"""

    name: Required[str]
    """Name is the unique identifier for the volume within the project"""

    type: Required[Literal["readOnly"]]
    """Type is the volume type (currently only "readOnly" is supported)"""


class Content(TypedDict, total=False):
    """Content specifies the content configuration for this volume"""

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
