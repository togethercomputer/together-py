# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "RolloutPreviewDefaultsParams",
    "BlueGreen",
    "Canary",
    "CanaryStep",
    "Metric",
    "MetricRegressionCheck",
    "MetricThresholdCheck",
    "Rolling",
]


class RolloutPreviewDefaultsParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    source_deployment_id: Required[Annotated[str, PropertyInfo(alias="sourceDeploymentId")]]
    """Deployment that traffic shifts away from."""

    target_deployment_id: Required[Annotated[str, PropertyInfo(alias="targetDeploymentId")]]
    """Deployment that traffic shifts toward."""

    blue_green: Annotated[BlueGreen, PropertyInfo(alias="blueGreen")]
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    canary: Canary
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

    metrics: Iterable[Metric]
    """Optional metric gates evaluated after each step's soak.

    Canary only; rejected on rolling and blue-green rollouts.
    """

    rolling: Rolling
    """
    Rolling strategy configuration for capacity-preserving batches that ramp target
    replicas up while draining source replicas.
    """


class BlueGreen(TypedDict, total=False):
    """
    Blue-green strategy configuration for a single cutover to the target deployment.
    """

    pass


class CanaryStep(TypedDict, total=False):
    """One stage of a canary rollout progression."""

    traffic: Required[int]
    """Required percentage of traffic on the target deployment for this step."""

    replicas: int
    """Optional explicit target replica count for this step."""


class Canary(TypedDict, total=False):
    """Canary strategy configuration for gradual traffic progression.

    An empty config uses the default 5, 25, 50, 100 percent ladder; over a frozen traffic-split pair left by cancel, the default ladder is derived at start from the pair's current served share so it begins above it.
    """

    step_interval: Annotated[str, PropertyInfo(alias="stepInterval")]
    """Optional positive soak between steps.

    Defaults to 3m if omitted, and grows to cover metric rule windows plus ingestion
    lag.
    """

    steps: Iterable[CanaryStep]
    """Optional progression steps.

    Defaults to 5, 25, 50, 100 percent when empty; explicit steps must increase and
    end at 100 percent.
    """


class MetricRegressionCheck(TypedDict, total=False):
    """
    Regression criteria that fail when the target regresses against the source beyond a limit.
    """

    direction: Required[Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]]
    """
    Required direction that indicates whether higher or lower metric values are
    worse.
    """

    max_regression_percent: Annotated[float, PropertyInfo(alias="maxRegressionPercent")]
    """Finite maximum allowed regression percentage, greater than or equal to 0.

    Omitting this value is read as 0. A value of 0 is the strictest budget; any
    regression fails, and exactly-at-budget passes.
    """


class MetricThresholdCheck(TypedDict, total=False):
    """
    Threshold criteria that fail when the target metric violates the configured bound.
    """

    operator: Required[
        Literal["THRESHOLD_OPERATOR_GT", "THRESHOLD_OPERATOR_GTE", "THRESHOLD_OPERATOR_LT", "THRESHOLD_OPERATOR_LTE"]
    ]
    """Required comparison operator applied to the target metric value."""

    value: float
    """Finite threshold value.

    Interpreted in the metric's unit: router_error_rate is a ratio in [0, 1],
    router_latency is milliseconds, and inflight_requests is in-flight requests per
    ready replica averaged over the rule window. Thresholds that no achievable value
    could pass, or that every achievable value passes, are rejected at create.

    Omitting this value is read as 0. Set 0 explicitly for the strictest threshold:
    nothing at all is tolerated.
    """


class Metric(TypedDict, total=False):
    """Metric gate evaluated during a rollout."""

    name: Required[Literal["inflight_requests", "router_error_rate", "router_latency"]]
    """Required catalogue key for the metric to gate on. `serving_latency` is retired."""

    percentile: int
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    regression_check: Annotated[MetricRegressionCheck, PropertyInfo(alias="regressionCheck")]
    """
    Regression criteria that fail when the target regresses against the source
    beyond a limit.
    """

    stat: Literal["METRIC_STAT_TYPE_AVG", "METRIC_STAT_TYPE_PERCENTILE"]
    """Aggregation used for the metric.

    Optional for router_error_rate and inflight_requests; omitted values default to
    METRIC_STAT_TYPE_AVG. Required for router_latency, where AVG or PERCENTILE may
    be used.
    """

    threshold_check: Annotated[MetricThresholdCheck, PropertyInfo(alias="thresholdCheck")]
    """
    Threshold criteria that fail when the target metric violates the configured
    bound.
    """

    window: str
    """Optional query window for the metric. Defaults to the step soak duration."""


class Rolling(TypedDict, total=False):
    """
    Rolling strategy configuration for capacity-preserving batches that ramp target replicas up while draining source replicas.
    """

    pass
