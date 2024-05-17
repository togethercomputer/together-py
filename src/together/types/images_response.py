# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["ImagesResponse", "Data"]


class Data(BaseModel):
    b64_json: str

    index: int


class ImagesResponse(BaseModel):
    id: str

    data: List[Data]

    model: str

    object: str
