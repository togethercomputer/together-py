# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .finetune_event import FinetuneEvent

__all__ = ["FineTuningListEventsResponse"]


class FineTuningListEventsResponse(BaseModel):
    data: List[FinetuneEvent]
