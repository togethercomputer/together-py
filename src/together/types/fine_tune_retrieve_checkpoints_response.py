# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["FineTuneRetrieveCheckpointsResponse", "Data"]


class Data(BaseModel):
    checkpoint_type: str

    created_at: str

    path: str

    step: int


class FineTuneRetrieveCheckpointsResponse(BaseModel):
    data: List[Data]
