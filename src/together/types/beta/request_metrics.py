# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["RequestMetrics"]


class RequestMetrics(BaseModel):
    """Request counts, rate, and status-code distribution over a time range."""

    failed_requests: Optional[str] = FieldInfo(alias="failedRequests", default=None)
    """Requests that failed during the time range."""

    requests_by_status_code: Optional[Dict[str, str]] = FieldInfo(alias="requestsByStatusCode", default=None)
    """Request counts keyed by HTTP status code."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average requests per second over the time range."""

    successful_requests: Optional[str] = FieldInfo(alias="successfulRequests", default=None)
    """Requests completed successfully during the time range."""

    total_requests: Optional[str] = FieldInfo(alias="totalRequests", default=None)
    """Total requests received during the time range."""
