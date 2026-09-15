# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = [
    "RolloutDefaultsPreview",
    "Spec",
    "SpecBlueGreen",
    "SpecCanary",
    "SpecCanaryStep",
    "SpecMetric",
    "SpecMetricRegressionCheck",
    "SpecMetricThresholdCheck",
    "SpecRolling",
    "Warning",
    "EstimatedEffectiveStep",
]


class SpecBlueGreen(BaseModel):
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    pass


class SpecCanaryStep(BaseModel):
    """One stage of a canary rollout progression."""

    traffic: int
    """Required percentage of traffic on the target deployment for this step."""

    replicas: Optional[int] = None
    """Optional explicit target replica count for this step."""


class SpecCanary(BaseModel):
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair left by cancel, the default ladder is derived at start from the pair's current served share so it begins above it.
    """

    step_interval: Optional[str] = FieldInfo(alias="stepInterval", default=None)
    """Optional positive soak between steps.

    Defaults to 3m if omitted, and grows to cover metric rule windows plus ingestion
    lag.
    """

    steps: Optional[List[SpecCanaryStep]] = None
    """Optional progression steps.

    Defaults to 5, 25, 50, 100 percent when empty; explicit steps must increase and
    end at 100 percent.
    """


class SpecMetricRegressionCheck(BaseModel):
    """
    Regression criteria that fail when the target regresses against the source beyond a limit.
    """

    direction: Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]
    """
    Required direction that indicates whether higher or lower metric values are
    worse.
    """

    max_regression_percent: Optional[float] = FieldInfo(alias="maxRegressionPercent", default=None)
    """Finite maximum allowed regression percentage, greater than or equal to 0.

    Omitting this value is read as 0. A value of 0 is the strictest budget; any
    regression fails, and exactly-at-budget passes.
    """


class SpecMetricThresholdCheck(BaseModel):
    """
    Threshold criteria that fail when the target metric violates the configured bound.
    """

    operator: Literal[
        "THRESHOLD_OPERATOR_GT", "THRESHOLD_OPERATOR_GTE", "THRESHOLD_OPERATOR_LT", "THRESHOLD_OPERATOR_LTE"
    ]
    """Required comparison operator applied to the target metric value."""

    value: Optional[float] = None
    """Finite threshold value.

    Interpreted in the metric's unit: router_error_rate is a ratio in [0, 1],
    router_latency is milliseconds, and inflight_requests is in-flight requests per
    ready replica averaged over the rule window. Thresholds that no achievable value
    could pass, or that every achievable value passes, are rejected at create.

    Omitting this value is read as 0. Set 0 explicitly for the strictest threshold:
    nothing at all is tolerated.
    """


class SpecMetric(BaseModel):
    """Metric gate evaluated during a rollout."""

    name: Literal["inflight_requests", "router_error_rate", "router_latency"]
    """Required catalogue key for the metric to gate on. `serving_latency` is retired."""

    percentile: Optional[int] = None
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    regression_check: Optional[SpecMetricRegressionCheck] = FieldInfo(alias="regressionCheck", default=None)
    """
    Regression criteria that fail when the target regresses against the source
    beyond a limit.
    """

    stat: Optional[Literal["METRIC_STAT_TYPE_AVG", "METRIC_STAT_TYPE_PERCENTILE"]] = None
    """Aggregation used for the metric.

    Optional for router_error_rate and inflight_requests; omitted values default to
    METRIC_STAT_TYPE_AVG. Required for router_latency, where AVG or PERCENTILE may
    be used.
    """

    threshold_check: Optional[SpecMetricThresholdCheck] = FieldInfo(alias="thresholdCheck", default=None)
    """
    Threshold criteria that fail when the target metric violates the configured
    bound.
    """

    window: Optional[str] = None
    """Optional query window for the metric. Defaults to the step soak duration."""


class SpecRolling(BaseModel):
    """
    Rolling strategy configuration for capacity-preserving batches that ramp target replicas up while draining source replicas.
    """

    pass


class Spec(BaseModel):
    """
    Strategy, metric gates, timing, and cleanup policy for shifting traffic between two deployments under one endpoint.
    """

    source_deployment_id: str = FieldInfo(alias="sourceDeploymentId")
    """Deployment that traffic shifts away from."""

    target_deployment_id: str = FieldInfo(alias="targetDeploymentId")
    """Deployment that traffic shifts toward."""

    blue_green: Optional[SpecBlueGreen] = FieldInfo(alias="blueGreen", default=None)
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    canary: Optional[SpecCanary] = None
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

    metrics: Optional[List[SpecMetric]] = None
    """Optional metric gates evaluated after each step's soak.

    Canary only; rejected on rolling and blue-green rollouts.
    """

    rolling: Optional[SpecRolling] = None
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


class EstimatedEffectiveStep(BaseModel):
    """One stage of a canary rollout progression."""

    traffic: int
    """Required percentage of traffic on the target deployment for this step."""

    replicas: Optional[int] = None
    """Optional explicit target replica count for this step."""


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

    estimated_effective_steps: Optional[List[EstimatedEffectiveStep]] = FieldInfo(
        alias="estimatedEffectiveSteps", default=None
    )
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
