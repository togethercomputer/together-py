# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["ModelListResponse", "ModelListResponseItem", "ModelListResponseItemPricing"]


class ModelListResponseItemPricing(BaseModel):
    base: float

    finetune: float

    hourly: float

    input: float

    output: float


class ModelListResponseItem(BaseModel):
    id: str

    created: int

    object: str

    type: Literal["chat", "language", "code", "image", "embedding", "moderation"]

    context_length: Optional[int] = None

    display_name: Optional[str] = None

    license: Optional[str] = None

    link: Optional[str] = None

    organization: Optional[str] = None

    pricing: Optional[ModelListResponseItemPricing] = None


ModelListResponse: TypeAlias = List[ModelListResponseItem]
