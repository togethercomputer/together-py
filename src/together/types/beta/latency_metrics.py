# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["LatencyMetrics"]


class LatencyMetrics(BaseModel):
    """
    Time-to-first-token, end-to-end, and inter-token latency percentiles in milliseconds.
    """

    itl_p50_ms: Optional[float] = FieldInfo(alias="itlP50Ms", default=None)
    """50th-percentile inter-token latency, in milliseconds."""

    itl_p90_ms: Optional[float] = FieldInfo(alias="itlP90Ms", default=None)
    """90th-percentile inter-token latency, in milliseconds."""

    itl_p99_ms: Optional[float] = FieldInfo(alias="itlP99Ms", default=None)
    """99th-percentile inter-token latency, in milliseconds."""

    latency_p50_ms: Optional[float] = FieldInfo(alias="latencyP50Ms", default=None)
    """50th-percentile end-to-end request latency, in milliseconds."""

    latency_p90_ms: Optional[float] = FieldInfo(alias="latencyP90Ms", default=None)
    """90th-percentile end-to-end request latency, in milliseconds."""

    latency_p99_ms: Optional[float] = FieldInfo(alias="latencyP99Ms", default=None)
    """99th-percentile end-to-end request latency, in milliseconds."""

    ttft_p50_ms: Optional[float] = FieldInfo(alias="ttftP50Ms", default=None)
    """50th-percentile time to first token, in milliseconds."""

    ttft_p90_ms: Optional[float] = FieldInfo(alias="ttftP90Ms", default=None)
    """90th-percentile time to first token, in milliseconds."""

    ttft_p99_ms: Optional[float] = FieldInfo(alias="ttftP99Ms", default=None)
    """99th-percentile time to first token, in milliseconds."""
