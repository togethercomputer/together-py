# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from ..._models import BaseModel
from .billing_usage_line_item import BillingUsageLineItem

__all__ = ["BillingUsageWindow"]


class BillingUsageWindow(BaseModel):
    date: str
    """Day this window covers (UTC, YYYY-MM-DD). Present for both granularities."""

    end_time: datetime
    """Window end (UTC, ISO 8601), exclusive.

    Start of the next day (daily) or hour (hourly).
    """

    line_items: List[BillingUsageLineItem]
    """Usage line items in this time window."""

    start_time: datetime
    """Window start (UTC, ISO 8601). Start of the day (daily) or hour (hourly)."""
