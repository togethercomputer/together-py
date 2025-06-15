# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .image_data_b64 import ImageDataB64
from .image_data_url import ImageDataURL

__all__ = ["ImageFile", "Data"]

Data: TypeAlias = Union[ImageDataB64, ImageDataURL]


class ImageFile(BaseModel):
    id: str

    data: List[Data]

    model: str

    object: Literal["list"]
