# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["LoRaTrainingType"]


class LoRaTrainingType(BaseModel):
    lora_alpha: int

    lora_r: int

    type: Literal["Lora"]

    lora_dropout: Optional[float] = None

    lora_trainable_modules: Optional[str] = None
