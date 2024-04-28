# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["ImagesResponse", "Image"]


class Image(BaseModel):
    metadata: Optional[Dict[str, object]] = None

    url: Optional[str] = None


class ImagesResponse(BaseModel):
    id: Optional[str] = None

    created: Optional[int] = None

    images: Optional[List[Image]] = None

    object: Optional[str] = None
