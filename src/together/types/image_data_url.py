# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ImageDataURL"]


class ImageDataURL(BaseModel):
    index: int

    type: Literal["url"]

    url: str
