# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ImageFile", "Data"]


class Data(BaseModel):
    index: int

    b64_json: Optional[str] = None

    url: Optional[str] = None


class ImageFile(BaseModel):
    id: str

    data: List[Data]

    model: str

    object: Literal["list"]
