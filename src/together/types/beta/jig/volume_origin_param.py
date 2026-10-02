# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .s3_origin_param import S3OriginParam

__all__ = ["VolumeOriginParam"]


class VolumeOriginParam(TypedDict, total=False):
    """External source Together copies into a new volume version."""

    s3: Required[S3OriginParam]
    """S3 bucket or prefix source for the volume sync."""
