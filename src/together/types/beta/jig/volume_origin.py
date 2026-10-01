# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .s3_origin import S3Origin
from ...._models import BaseModel

__all__ = ["VolumeOrigin"]


class VolumeOrigin(BaseModel):
    """External source Together copies into a new volume version."""

    s3: S3Origin
    """S3 bucket or prefix source for the volume sync."""
