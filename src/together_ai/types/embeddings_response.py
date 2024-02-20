# File generated from our OpenAPI spec by Stainless.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["EmbeddingsResponse", "Data"]


class Data(BaseModel):
    embedding: Optional[List[float]] = None

    index: Optional[int] = None

    object: Optional[Literal["embedding"]] = None


class EmbeddingsResponse(BaseModel):
    data: List[Data]

    model: str

    object: Literal["list"]
