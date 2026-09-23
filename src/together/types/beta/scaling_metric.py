# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ScalingMetric"]


class ScalingMetric(BaseModel):
    """Metric and target used by the autoscaler to recommend a replica count."""

    name: Literal[
        "active_sessions",
        "cache_hit_rate",
        "decoding_speed",
        "e2e_latency",
        "gpu_utilization",
        "inflight_requests",
        "throughput_per_replica",
        "token_utilization",
        "ttft",
    ]
    """Autoscaling metric name from the server allowlist."""

    target: float
    """Target interpreted according to `type`.

    Utilization uses a percentage from 0 to 100, value uses an absolute measurement,
    and average value uses a per-replica measurement.
    """

    type: Literal["METRIC_TARGET_TYPE_VALUE", "METRIC_TARGET_TYPE_UTILIZATION", "METRIC_TARGET_TYPE_AVERAGE_VALUE"]
    """
    Whether `target` is an absolute value, a utilization percentage, or a
    per-replica average.
    """

    percentile: Optional[str] = None
    """
    Percentile to evaluate for latency-based metrics: `p50`, `p90`, `p95`, or `p99`.
    """
