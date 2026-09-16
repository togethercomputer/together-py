# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .scaling_rules_param import ScalingRulesParam
from .scaling_metric_param import ScalingMetricParam

__all__ = ["DeploymentAutoscalingParam"]


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

    scale_down: Annotated[ScalingRulesParam, PropertyInfo(alias="scaleDown")]
    """Rate limits applied after stabilization and before replica bounds."""

    scale_down_window: Annotated[str, PropertyInfo(alias="scaleDownWindow")]
    """Time a lower replica recommendation must remain stable before scaling down.

    Defaults to `5m`.
    """

    scale_to_zero_window: Annotated[str, PropertyInfo(alias="scaleToZeroWindow")]
    """
    Idle period after which the deployment automatically stops and releases its
    replicas.
    """

    scale_up: Annotated[ScalingRulesParam, PropertyInfo(alias="scaleUp")]
    """Rate limits applied after stabilization and before replica bounds."""

    scale_up_window: Annotated[str, PropertyInfo(alias="scaleUpWindow")]
    """Stabilization window before scaling up."""

    scaling_metrics: Annotated[Iterable[ScalingMetricParam], PropertyInfo(alias="scalingMetrics")]
    """Metrics and targets that drive replica recommendations.

    When omitted, the platform uses concurrent in-flight requests per replica.
    """
