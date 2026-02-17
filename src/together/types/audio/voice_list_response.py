# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["VoiceListResponse", "Data", "DataVoice"]


class DataVoice(BaseModel):
    id: str

    name: str
    """Voice name to be used for audio inference."""


class Data(BaseModel):
    """Represents a model with its available voices."""

    model: str
    """Model name."""

    voices: List[DataVoice]
    """List of available voices for the model."""


class VoiceListResponse(BaseModel):
    """Response containing a list of models and their available voices."""

    data: List[Data]
