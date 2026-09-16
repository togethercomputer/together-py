# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .metric_rule import MetricRule
from .rollout_step import RolloutStep
from .canary_config import CanaryConfig
from .rolling_config import RollingConfig
from .blue_green_config import BlueGreenConfig

__all__ = ["RolloutDefaultsPreview", "Spec", "Warning"]


class Spec(BaseModel):
    """
    Strategy, metric gates, timing, and cleanup policy for shifting traffic between two deployments under one endpoint.
    """

    source_deployment_id: str = FieldInfo(alias="sourceDeploymentId")
    """Deployment that traffic shifts away from."""

    target_deployment_id: str = FieldInfo(alias="targetDeploymentId")
    """Deployment that traffic shifts toward."""

    blue_green: Optional[BlueGreenConfig] = FieldInfo(alias="blueGreen", default=None)
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    canary: Optional[CanaryConfig] = None
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen
    traffic-split pair left by cancel, the default ladder is derived at start from
    the pair's current served share so it begins above it.
    """

    final_source_replicas: Optional[int] = FieldInfo(alias="finalSourceReplicas", default=None)
    """Optional final replica count for the source deployment.

    Defaults to 0, which drains and stops the source.
    """

    final_target_replicas: Optional[int] = FieldInfo(alias="finalTargetReplicas", default=None)
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

    metrics: Optional[List[MetricRule]] = None
    """Optional metric gates evaluated after each step's soak.

    Canary only; rejected on rolling and blue-green rollouts.
    """

    rolling: Optional[RollingConfig] = None
    """
    Rolling strategy configuration for capacity-preserving batches that ramp target
    replicas up while draining source replicas.
    """


class Warning(BaseModel):
    """A non-blocking finding attached to a rollout defaults preview."""

    code: str
    """
    Machine-readable warning code, such as START_WILL_REJECT,
    ROLLOUT_WILL_RAISE_TARGET_MAX, FINAL_BELOW_INHERITED_MIN, or
    FINAL_BELOW_SOURCE_MIN. Render message for unrecognized codes.
    """

    message: str
    """Plain-language description of the finding, safe to show users as-is."""


class RolloutDefaultsPreview(BaseModel):
    """
    Completed create-form state — the caller's spec with defaulted values filled in, the steps the rollout is expected to walk, and the capacity context the defaults were computed from. Display only.
    """

    source_replicas: int = FieldInfo(alias="sourceReplicas")
    """Source deployment replica count the defaults were computed from.

    Zero is a real value.
    """

    spec: Spec
    """
    Strategy, metric gates, timing, and cleanup policy for shifting traffic between
    two deployments under one endpoint.
    """

    target_max_replicas: int = FieldInfo(alias="targetMaxReplicas")
    """Target deployment autoscaling maximum replica count. Zero is a real value."""

    target_min_replicas: int = FieldInfo(alias="targetMinReplicas")
    """Target deployment autoscaling minimum replica count. Zero is a real value."""

    target_replicas: int = FieldInfo(alias="targetReplicas")
    """Target deployment replica count the defaults were computed from.

    Zero is a real value.
    """

    warnings: List[Warning]
    """Non-blocking findings to surface next to the form.

    An empty list means the shown values are safe to submit as-is.
    """

    estimated_effective_steps: Optional[List[RolloutStep]] = FieldInfo(alias="estimatedEffectiveSteps", default=None)
    """Steps the rollout is expected to walk when the caller leaves steps unset.

    Display only. Empty when the caller supplied steps or no ladder applies.
    """

    estimated_seed_percent: Optional[int] = FieldInfo(alias="estimatedSeedPercent", default=None)
    """
    Percentage of the pair's traffic currently reaching the target, the floor the
    suggested steps start above. Unset when not a frozen pair or unknown; 0 is a
    real measurement.
    """

    frozen_pair: Optional[bool] = FieldInfo(alias="frozenPair", default=None)
    """
    True when both deployments stand in the endpoint traffic split, so the rollout
    resumes from the current split rather than from zero. See warnings for standing
    split shapes that StartRollout will still reject.
    """
