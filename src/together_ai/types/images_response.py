# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ImagesResponse", "Data"]


class Data(BaseModel):
    b64_json: Optional[str] = None

    index: Optional[int] = None


class ImagesResponse(BaseModel):
    id: Optional[str] = None

    created: Optional[int] = None

    data: Optional[List[Data]] = None

    model: Optional[str] = None

    object: Optional[str] = None
