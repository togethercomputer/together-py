# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .billing_usage_window import BillingUsageWindow

__all__ = ["BillingUsageReport"]


class BillingUsageReport(BaseModel):
    billing_period: str
    """Billing month (YYYY-MM)."""

    currency: Literal["USD"]

    data: List[BillingUsageWindow]
    """Time windows containing usage line items."""

    earliest_window_start: Optional[datetime] = None
    """
    Start of the earliest time window with usage in the month (UTC, ISO 8601); null
    when the month has no usage.
    """

    latest_window_end: Optional[datetime] = None
    """
    Exclusive end of the latest time window with usage in the month (UTC, ISO 8601);
    null when the month has no usage. Describes the whole month, not the current
    page.
    """

    next_cursor: Optional[str] = None
    """Opaque cursor for the next page; null when this is the last page."""

    object: Literal["list"]

    organization_id: str
    """ID of the organization the report belongs to."""
