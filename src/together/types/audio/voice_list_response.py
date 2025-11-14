# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["VoiceListResponse", "Data", "DataVoice"]


class DataVoice(BaseModel):
    id: str

    name: str


class Data(BaseModel):
    model: str

    voices: List[DataVoice]


class VoiceListResponse(BaseModel):
    data: List[Data]
