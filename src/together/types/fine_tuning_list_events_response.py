# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .fine_tune_event import FineTuneEvent

__all__ = ["FineTuningListEventsResponse"]


class FineTuningListEventsResponse(BaseModel):
    data: List[FineTuneEvent]
