# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EmbeddingsResponse", "Data"]


class Data(BaseModel):
    embedding: List[float]

    index: int

    object: Literal["embedding"]


class EmbeddingsResponse(BaseModel):
    data: List[Data]

    model: str

    object: Literal["list"]
