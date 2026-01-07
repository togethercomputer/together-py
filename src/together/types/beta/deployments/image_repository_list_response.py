# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["ImageRepositoryListResponse", "Data"]


class Data(BaseModel):
    id: Optional[str] = None
    """
    ID is the unique identifier for this repository (repository name with slashes
    replaced by "\\__\\__\\__")
    """

    object: Optional[str] = None
    """Object is the type identifier for this response (always "image-repository")"""

    url: Optional[str] = None
    """
    URL is the full registry URL for this repository (e.g.,
    "registry.together.ai/project-id/repository-name")
    """


class ImageRepositoryListResponse(BaseModel):
    data: Optional[List[Data]] = None
    """Data is the array of repository items"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "list")"""
