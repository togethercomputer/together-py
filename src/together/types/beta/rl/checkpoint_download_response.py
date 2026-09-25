# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ...._models import BaseModel
from .checkpoint_file import CheckpointFile

__all__ = ["CheckpointDownloadResponse"]


class CheckpointDownloadResponse(BaseModel):
    """Presigned download URLs for a checkpoint's files"""

    data: List[CheckpointFile]
    """List of files with presigned download URLs"""
