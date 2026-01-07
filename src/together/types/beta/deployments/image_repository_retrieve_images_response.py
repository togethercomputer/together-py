# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["ImageRepositoryRetrieveImagesResponse", "Data"]


class Data(BaseModel):
    object: Optional[str] = None
    """Object is the type identifier for this response (always "image")"""

    tag: Optional[str] = None
    """Tag is the image tag/version identifier (e.g., "latest", "v1.0.0")"""

    url: Optional[str] = None
    """
    URL is the full registry URL for this image including tag (e.g.,
    "registry.together.ai/project-id/repository:tag")
    """


class ImageRepositoryRetrieveImagesResponse(BaseModel):
    data: Optional[List[Data]] = None
    """Data is the array of image items"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "list")"""
