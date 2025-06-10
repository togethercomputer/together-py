# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["LoRaTrainingTypeParam"]


class LoRaTrainingTypeParam(TypedDict, total=False):
    lora_alpha: Required[int]

    lora_r: Required[int]

    type: Required[Literal["Lora"]]

    lora_dropout: float

    lora_trainable_modules: str
