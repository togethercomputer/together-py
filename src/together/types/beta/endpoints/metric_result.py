# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["MetricResult"]


class MetricResult(BaseModel):
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
