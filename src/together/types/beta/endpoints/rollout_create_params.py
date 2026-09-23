# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .metric_rule_param import MetricRuleParam
from .canary_config_param import CanaryConfigParam
from .rolling_config_param import RollingConfigParam
from .blue_green_config_param import BlueGreenConfigParam

__all__ = ["RolloutCreateParams"]


class RolloutCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    source_deployment_id: Required[Annotated[str, PropertyInfo(alias="sourceDeploymentId")]]
    """Deployment that traffic shifts away from."""

    target_deployment_id: Required[Annotated[str, PropertyInfo(alias="targetDeploymentId")]]
    """Deployment that traffic shifts toward."""

    blue_green: Annotated[BlueGreenConfigParam, PropertyInfo(alias="blueGreen")]
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    canary: CanaryConfigParam
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen
    traffic-split pair left by cancel, the default ladder is derived at start from
    the pair's current served share so it begins above it.
    """

    final_source_replicas: Annotated[int, PropertyInfo(alias="finalSourceReplicas")]
    """Optional final replica count for the source deployment.

    Defaults to 0, which drains and stops the source.
    """

    final_target_replicas: Annotated[int, PropertyInfo(alias="finalTargetReplicas")]
    """Optional target replica floor at completion.

    Must be at least 1 when set; defaults to the source deployment's replica count
    at create time, or to the source and target deployments' combined replica count
    when both already stand in the endpoint traffic split after a cancel. The
    completed target's autoscaling max lands at the landing ceiling, max(this value,
    the source max, the target's own max); the rollout may lift the target max at
    first wake, at the first step that needs it, or at completion unless an operator
    changes max mid-run. The lifted ceiling remains after completion, and
    PreviewRolloutDefaults reports a coming lift as ROLLOUT_WILL_RAISE_TARGET_MAX. A
    pre-existing target whose own autoscaling min is higher keeps that floor,
    reported as FINAL_BELOW_INHERITED_MIN. A target that starts stopped lands
    exactly at this value; if the source min was higher, PreviewRolloutDefaults
    reports FINAL_BELOW_SOURCE_MIN.
    """

    metrics: Iterable[MetricRuleParam]
    """Optional metric gates evaluated after each step's soak.

    Canary only; rejected on rolling and blue-green rollouts.
    """

    rolling: RollingConfigParam
    """
    Rolling strategy configuration for capacity-preserving batches that ramp target
    replicas up while draining source replicas.
    """
