# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["FineTuneListEventsResponse", "FineTuneListEventsResponseItem"]


class FineTuneListEventsResponseItem(BaseModel):
    details: Optional[Dict[str, object]] = None

    event: Optional[str] = None

    timestamp: Optional[int] = None


FineTuneListEventsResponse = List[FineTuneListEventsResponseItem]
