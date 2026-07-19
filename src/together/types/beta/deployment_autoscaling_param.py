# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DeploymentAutoscalingParam", "ScalingMetric"]


class ScalingMetric(TypedDict, total=False):
    """Metric and target used by the autoscaler to recommend a replica count."""

    name: Required[str]
    """
    Metric name, such as `gpu_utilization`, `ttft`, `inflight_requests`,
    `e2e_latency`, `throughput_per_replica`, or `decoding_speed`.
    """

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


class DeploymentAutoscalingParam(TypedDict, total=False):
    """Autoscaling configuration for a deployment."""

    max_replicas: Annotated[int, PropertyInfo(alias="maxReplicas")]
    """Maximum number of replicas.

    Defaults to `minReplicas`; omitting it on update preserves the current value.
    """

    min_replicas: Annotated[int, PropertyInfo(alias="minReplicas")]
    """Minimum number of replicas.

    Omit on update to preserve the current value. Set both `minReplicas` and
    `maxReplicas` to `0` to stop the deployment.
    """

    scale_down_window: Annotated[str, PropertyInfo(alias="scaleDownWindow")]
    """Time a lower replica recommendation must remain stable before scaling down.

    Defaults to `5m`.
    """

    scale_to_zero_window: Annotated[str, PropertyInfo(alias="scaleToZeroWindow")]
    """
    Idle period after which the deployment automatically stops and releases its
    replicas.
    """

    scale_up_window: Annotated[str, PropertyInfo(alias="scaleUpWindow")]
    """Stabilization window before scaling up."""

    scaling_metrics: Annotated[Iterable[ScalingMetric], PropertyInfo(alias="scalingMetrics")]
    """Metrics and targets that drive replica recommendations.

    When omitted, the platform uses concurrent in-flight requests per replica.
    """
