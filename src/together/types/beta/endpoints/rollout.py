# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = [
    "Rollout",
    "Status",
    "StatusStep",
    "StatusStepMetric",
    "StatusCondition",
    "StatusConditionMetric",
    "PauseInfo",
]


class StatusStepMetric(BaseModel):
    """
    Observed metric result enriched with rollout rule criteria and the rule's recorded verdict. Unmeasured rules are synthesized with verdict METRIC_VERDICT_UNAVAILABLE and no source or target value.
    """

    check: Optional[Literal["METRIC_CHECK_TYPE_THRESHOLD", "METRIC_CHECK_TYPE_REGRESSION"]] = None
    """Evaluation form used by the metric rule."""

    direction: Optional[Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]] = None
    """Direction that indicates whether higher or lower values are worse."""

    failure_reason: Optional[str] = FieldInfo(alias="failureReason", default=None)
    """Rule-specific failure text.

    Set only when verdict is METRIC_VERDICT_BREACHED and the gate recorded one.
    """

    max_regression_percent: Optional[float] = FieldInfo(alias="maxRegressionPercent", default=None)
    """Regression percentage limit used when check is METRIC_CHECK_TYPE_REGRESSION."""

    name: Optional[str] = None
    """Metric name as exported to the observability backend."""

    operator: Optional[
        Literal["THRESHOLD_OPERATOR_GT", "THRESHOLD_OPERATOR_GTE", "THRESHOLD_OPERATOR_LT", "THRESHOLD_OPERATOR_LTE"]
    ] = None
    """Threshold comparison operator."""

    percentile: Optional[int] = None
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    source_value: Optional[float] = FieldInfo(alias="sourceValue", default=None)
    """Observed source baseline.

    Set only for regression checks with a recorded observation; a 0 reading
    serializes explicitly.
    """

    stat: Optional[Literal["METRIC_STAT_TYPE_AVG", "METRIC_STAT_TYPE_PERCENTILE"]] = None
    """Aggregation used for the metric."""

    target_value: Optional[float] = FieldInfo(alias="targetValue", default=None)
    """Observed target value.

    Set when the gate recorded an observation; absent on synthesized unavailable
    results. A 0 reading serializes explicitly.
    """

    threshold: Optional[float] = None
    """Threshold criteria used when check is METRIC_CHECK_TYPE_THRESHOLD."""

    verdict: Optional[Literal["METRIC_VERDICT_PASS", "METRIC_VERDICT_BREACHED", "METRIC_VERDICT_UNAVAILABLE"]] = None
    """Rule decision recorded by the metric gate.

    Absent when no decision was recorded.
    """


class StatusStep(BaseModel):
    """Collapsed execution state for one rollout step."""

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
    """Timestamp when this step finished, was skipped over, or the rollout ended on it.

    Unset while in progress.
    """

    failure_reason: Optional[str] = FieldInfo(alias="failureReason", default=None)
    """Failure reason set only when this step failed."""

    metrics: Optional[List[StatusStepMetric]] = None
    """Metric gate results for this step, enriched with criteria and verdict.

    Unmeasured rules appear as synthesized rows with verdict
    METRIC_VERDICT_UNAVAILABLE and no measured values.
    """

    started_at: Optional[datetime] = FieldInfo(alias="startedAt", default=None)
    """Timestamp when this step's first sub-step ran.

    Unset for steps no sub-step reached.
    """

    state: Optional[
        Literal[
            "ROLLOUT_STEP_STATE_PENDING",
            "ROLLOUT_STEP_STATE_RUNNING",
            "ROLLOUT_STEP_STATE_PASSED",
            "ROLLOUT_STEP_STATE_FAILED",
            "ROLLOUT_STEP_STATE_PAUSED",
            "ROLLOUT_STEP_STATE_CANCELED",
            "ROLLOUT_STEP_STATE_SKIPPED",
        ]
    ] = None
    """Outcome of this step.

    Finished steps are PASSED, the live step mirrors the rollout state, skipped-over
    steps are SKIPPED, and unreached steps are PENDING.
    """

    step_index: Optional[int] = FieldInfo(alias="stepIndex", default=None)
    """Index of this step in the rollout progression. Step 0 serializes explicitly."""

    target_traffic_percent: Optional[int] = FieldInfo(alias="targetTrafficPercent", default=None)
    """Target traffic percentage configured for this step.

    Always serializes for recorded steps.
    """


class StatusConditionMetric(BaseModel):
    """
    Observed metric result enriched with rollout rule criteria and the rule's recorded verdict. Unmeasured rules are synthesized with verdict METRIC_VERDICT_UNAVAILABLE and no source or target value.
    """

    check: Optional[Literal["METRIC_CHECK_TYPE_THRESHOLD", "METRIC_CHECK_TYPE_REGRESSION"]] = None
    """Evaluation form used by the metric rule."""

    direction: Optional[Literal["REGRESSION_DIRECTION_HIGHER_IS_WORSE", "REGRESSION_DIRECTION_LOWER_IS_WORSE"]] = None
    """Direction that indicates whether higher or lower values are worse."""

    failure_reason: Optional[str] = FieldInfo(alias="failureReason", default=None)
    """Rule-specific failure text.

    Set only when verdict is METRIC_VERDICT_BREACHED and the gate recorded one.
    """

    max_regression_percent: Optional[float] = FieldInfo(alias="maxRegressionPercent", default=None)
    """Regression percentage limit used when check is METRIC_CHECK_TYPE_REGRESSION."""

    name: Optional[str] = None
    """Metric name as exported to the observability backend."""

    operator: Optional[
        Literal["THRESHOLD_OPERATOR_GT", "THRESHOLD_OPERATOR_GTE", "THRESHOLD_OPERATOR_LT", "THRESHOLD_OPERATOR_LTE"]
    ] = None
    """Threshold comparison operator."""

    percentile: Optional[int] = None
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    source_value: Optional[float] = FieldInfo(alias="sourceValue", default=None)
    """Observed source baseline.

    Set only for regression checks with a recorded observation; a 0 reading
    serializes explicitly.
    """

    stat: Optional[Literal["METRIC_STAT_TYPE_AVG", "METRIC_STAT_TYPE_PERCENTILE"]] = None
    """Aggregation used for the metric."""

    target_value: Optional[float] = FieldInfo(alias="targetValue", default=None)
    """Observed target value.

    Set when the gate recorded an observation; absent on synthesized unavailable
    results. A 0 reading serializes explicitly.
    """

    threshold: Optional[float] = None
    """Threshold criteria used when check is METRIC_CHECK_TYPE_THRESHOLD."""

    verdict: Optional[Literal["METRIC_VERDICT_PASS", "METRIC_VERDICT_BREACHED", "METRIC_VERDICT_UNAVAILABLE"]] = None
    """Rule decision recorded by the metric gate.

    Absent when no decision was recorded.
    """


class StatusCondition(BaseModel):
    """Structured reason a rollout stopped progressing."""

    at_step: Optional[int] = FieldInfo(alias="atStep", default=None)
    """Step index where the condition arose. Step 0 serializes explicitly."""

    category: Optional[
        Literal[
            "ROLLOUT_FAILURE_CATEGORY_METRIC_REGRESSION",
            "ROLLOUT_FAILURE_CATEGORY_METRICS_UNAVAILABLE",
            "ROLLOUT_FAILURE_CATEGORY_TARGET_NOT_READY",
            "ROLLOUT_FAILURE_CATEGORY_SOURCE_NOT_DRAINED",
            "ROLLOUT_FAILURE_CATEGORY_HEALTH_REGRESSION",
            "ROLLOUT_FAILURE_CATEGORY_CAPACITY_EXHAUSTED",
            "ROLLOUT_FAILURE_CATEGORY_ROUTING_ERROR",
            "ROLLOUT_FAILURE_CATEGORY_DEPENDENCY_OUTAGE",
            "ROLLOUT_FAILURE_CATEGORY_ABORTED_BY_OPERATOR",
            "ROLLOUT_FAILURE_CATEGORY_INTERNAL",
            "ROLLOUT_FAILURE_CATEGORY_POLICY_INFEASIBLE",
            "ROLLOUT_FAILURE_CATEGORY_UNDER_SERVED",
            "ROLLOUT_FAILURE_CATEGORY_ENTITLEMENT_LAPSED",
        ]
    ] = None
    """Category that classifies why the rollout stopped."""

    message: Optional[str] = None
    """Human-readable explanation for the condition."""

    metrics: Optional[List[StatusConditionMetric]] = None
    """Metrics observed at the failing gate, enriched with their criteria.

    Unmeasured rules appear as synthesized rows with verdict
    METRIC_VERDICT_UNAVAILABLE and no measured values.
    """

    observed_at: Optional[datetime] = FieldInfo(alias="observedAt", default=None)
    """Timestamp when the condition was observed."""

    type: Optional[Literal["CapacityLimited"]] = None
    """Informational condition type.

    `CapacityLimited` means the current step advanced partially because full
    capacity was not placeable.
    """


class Status(BaseModel):
    """Derived runtime progress for a rollout."""

    steps: List[StatusStep]
    """Per-step rollout execution summaries."""

    total_steps: int = FieldInfo(alias="totalSteps")
    """Total number of steps in the rollout progression.

    Always serializes when status is present.
    """

    condition: Optional[StatusCondition] = None
    """Structured reason a rollout stopped progressing."""

    conditions: Optional[List[StatusCondition]] = None
    """Informational conditions that describe the rollout's current state.

    Omitted when empty; clients should treat an absent key as an empty list.
    """

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """Timestamp of the most recent progress update."""


class PauseInfo(BaseModel):
    """Pause metadata returned while a rollout is paused."""

    paused_at: datetime = FieldInfo(alias="pausedAt")
    """Timestamp when the rollout was paused."""

    reason: Optional[str] = None
    """Human-readable reason recorded when the rollout was paused."""


class Rollout(BaseModel):
    """
    Public view of a rollout resource, including runtime progress and any pause or abort reason.
    """

    id: str
    """Output only. Unique rollout identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Output only. Timestamp when the rollout was created."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. Endpoint this rollout belongs to."""

    source_deployment_id: str = FieldInfo(alias="sourceDeploymentId")
    """Output only. Deployment that traffic is shifting away from."""

    state: Literal[
        "ROLLOUT_STATE_RUNNING",
        "ROLLOUT_STATE_PAUSED",
        "ROLLOUT_STATE_STABILIZING",
        "ROLLOUT_STATE_COMPLETED",
        "ROLLOUT_STATE_PENDING",
        "ROLLOUT_STATE_SYSTEM_PAUSED",
        "ROLLOUT_STATE_CANCELLING",
        "ROLLOUT_STATE_CANCELED",
        "ROLLOUT_STATE_PAUSING",
    ]
    """Output only. High-level rollout lifecycle state."""

    status: Status
    """Derived runtime progress for a rollout."""

    strategy: Literal[
        "ROLLOUT_STRATEGY_TYPE_ROLLING", "ROLLOUT_STRATEGY_TYPE_CANARY", "ROLLOUT_STRATEGY_TYPE_BLUE_GREEN"
    ]
    """Output only. Rollout strategy selected at creation."""

    target_deployment_id: str = FieldInfo(alias="targetDeploymentId")
    """Output only. Deployment that traffic is shifting toward."""

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
    """Output only. Timestamp when the rollout reached a terminal state."""

    current_step: Optional[int] = FieldInfo(alias="currentStep", default=None)
    """Output only.

    Zero-based index of the current step. Unset while PENDING; step 0 is reported
    explicitly after start.
    """

    current_traffic_percent: Optional[int] = FieldInfo(alias="currentTrafficPercent", default=None)
    """Output only. Applied percentage of traffic on the target deployment."""

    etag: Optional[str] = None
    """Output only. Opaque version tag for optimistic concurrency control."""

    pause_info: Optional[PauseInfo] = FieldInfo(alias="pauseInfo", default=None)
    """Pause metadata returned while a rollout is paused."""

    started_at: Optional[datetime] = FieldInfo(alias="startedAt", default=None)
    """Output only. Timestamp when the rollout started running."""
