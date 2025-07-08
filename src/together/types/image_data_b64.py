# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ImageDataB64"]


class ImageDataB64(BaseModel):
    b64_json: str

    index: int

    type: Literal["b64_json"]
