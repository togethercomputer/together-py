# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union

from ...._models import BaseModel

__all__ = ["CheckpointDownloadResponse", "Data"]


class Data(BaseModel):
    """A downloadable file within a checkpoint"""

    filename: str
    """Name of the file"""

    size: Union[str, int]
    """File size in bytes"""

    url: str
    """Presigned URL for downloading the file"""


class CheckpointDownloadResponse(BaseModel):
    """Presigned download URLs for a checkpoint's files"""

    data: List[Data]
    """List of files with presigned download URLs"""
