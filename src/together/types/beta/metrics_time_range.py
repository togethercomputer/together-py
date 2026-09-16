# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MetricsTimeRange"]


class MetricsTimeRange(BaseModel):
    """Closed-open time range used by metrics and analytics responses."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""
