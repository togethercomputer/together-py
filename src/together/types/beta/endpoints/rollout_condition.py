# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .metric_result import MetricResult

__all__ = ["RolloutCondition"]


class RolloutCondition(BaseModel):
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

    metrics: Optional[List[MetricResult]] = None
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
