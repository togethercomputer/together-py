# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union

from ...._models import BaseModel

__all__ = ["CheckpointFile"]


class CheckpointFile(BaseModel):
    """A downloadable file within a checkpoint"""

    filename: str
    """Name of the file"""

    size: Union[str, int]
    """File size in bytes"""

    url: str
    """Presigned URL for downloading the file"""
