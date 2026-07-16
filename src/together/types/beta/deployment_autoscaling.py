# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DeploymentAutoscaling", "ScalingMetric"]


class ScalingMetric(BaseModel):
    """Metric and target used by the autoscaler to recommend a replica count."""

    name: str
    """
    Metric name, such as `gpu_utilization`, `ttft`, `inflight_requests`,
    `e2e_latency`, `throughput_per_replica`, or `decoding_speed`.
    """

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


class DeploymentAutoscaling(BaseModel):
    """Autoscaling configuration for a deployment."""

    max_replicas: Optional[int] = FieldInfo(alias="maxReplicas", default=None)
    """Maximum number of replicas.

    Defaults to `minReplicas`; omitting it on update preserves the current value.
    """

    min_replicas: Optional[int] = FieldInfo(alias="minReplicas", default=None)
    """Minimum number of replicas.

    Omit on update to preserve the current value. Set both `minReplicas` and
    `maxReplicas` to `0` to stop the deployment.
    """

    scale_down_window: Optional[str] = FieldInfo(alias="scaleDownWindow", default=None)
    """Time a lower replica recommendation must remain stable before scaling down.

    Defaults to `5m`.
    """

    scale_to_zero_window: Optional[str] = FieldInfo(alias="scaleToZeroWindow", default=None)
    """
    Idle period after which the deployment automatically stops and releases its
    replicas.
    """

    scale_up_window: Optional[str] = FieldInfo(alias="scaleUpWindow", default=None)
    """Stabilization window before scaling up."""

    scaling_metrics: Optional[List[ScalingMetric]] = FieldInfo(alias="scalingMetrics", default=None)
    """Metrics and targets that drive replica recommendations.

    When omitted, the platform uses concurrent in-flight requests per replica.
    """
