# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ModelObject", "Pricing"]


class Pricing(BaseModel):
    base: float

    finetune: float

    hourly: float

    input: float

    output: float


class ModelObject(BaseModel):
    id: str

    created: int

    object: str

    type: Literal["chat", "language", "code", "image", "embedding", "moderation", "rerank"]

    context_length: Optional[int] = None

    display_name: Optional[str] = None

    license: Optional[str] = None

    link: Optional[str] = None

    organization: Optional[str] = None

    pricing: Optional[Pricing] = None
