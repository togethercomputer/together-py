# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .scaling_rules import ScalingRules
from .scaling_metric import ScalingMetric

__all__ = ["DeploymentAutoscaling"]


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

    scale_down: Optional[ScalingRules] = FieldInfo(alias="scaleDown", default=None)
    """Rate limits applied after stabilization and before replica bounds."""

    scale_down_window: Optional[str] = FieldInfo(alias="scaleDownWindow", default=None)
    """Time a lower replica recommendation must remain stable before scaling down.

    Defaults to `5m`.
    """

    scale_to_zero_window: Optional[str] = FieldInfo(alias="scaleToZeroWindow", default=None)
    """
    Idle period after which the deployment automatically stops and releases its
    replicas.
    """

    scale_up: Optional[ScalingRules] = FieldInfo(alias="scaleUp", default=None)
    """Rate limits applied after stabilization and before replica bounds."""

    scale_up_window: Optional[str] = FieldInfo(alias="scaleUpWindow", default=None)
    """Stabilization window before scaling up."""

    scaling_metrics: Optional[List[ScalingMetric]] = FieldInfo(alias="scalingMetrics", default=None)
    """Metrics and targets that drive replica recommendations.

    When omitted, the platform uses concurrent in-flight requests per replica.
    """
