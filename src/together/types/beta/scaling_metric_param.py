# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ScalingMetricParam"]


class ScalingMetricParam(TypedDict, total=False):
    """Metric and target used by the autoscaler to recommend a replica count."""

    name: Required[
        Literal[
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
    ]
    """Autoscaling metric name from the server allowlist."""

    target: Required[float]
    """Target interpreted according to `type`.

    Utilization uses a percentage from 0 to 100, value uses an absolute measurement,
    and average value uses a per-replica measurement.
    """

    type: Required[
        Literal["METRIC_TARGET_TYPE_VALUE", "METRIC_TARGET_TYPE_UTILIZATION", "METRIC_TARGET_TYPE_AVERAGE_VALUE"]
    ]
    """
    Whether `target` is an absolute value, a utilization percentage, or a
    per-replica average.
    """

    percentile: str
    """
    Percentile to evaluate for latency-based metrics: `p50`, `p90`, `p95`, or `p99`.
    """
