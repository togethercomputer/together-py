# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .metric_result import MetricResult

__all__ = ["RolloutStepStatus"]


class RolloutStepStatus(BaseModel):
    """Collapsed execution state for one rollout step."""

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
    """Timestamp when this step finished, was skipped over, or the rollout ended on it.

    Unset while in progress.
    """

    failure_reason: Optional[str] = FieldInfo(alias="failureReason", default=None)
    """Failure reason set only when this step failed."""

    metrics: Optional[List[MetricResult]] = None
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
