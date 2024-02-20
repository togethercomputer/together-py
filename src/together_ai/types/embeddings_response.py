# File generated from our OpenAPI spec by Stainless.

from typing import Optional, List

from typing_extensions import Literal

from typing import Optional, Union, List, Dict, Any
from typing_extensions import Literal
from pydantic import Field as FieldInfo
from .._models import BaseModel
from ..types import shared

__all__ = ["EmbeddingsResponse", "Data"]

class Data(BaseModel):
    embedding: Optional[List[float]] = None

    index: Optional[int] = None

    object: Optional[Literal["embedding"]] = None

class EmbeddingsResponse(BaseModel):
    data: List[Data]

    model: str

    object: Literal["list"]