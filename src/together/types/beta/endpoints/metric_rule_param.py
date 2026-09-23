# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from .threshold_check_param import ThresholdCheckParam
from .regression_check_param import RegressionCheckParam

__all__ = ["MetricRuleParam"]


class MetricRuleParam(TypedDict, total=False):
    """Metric gate evaluated during a rollout."""

    name: Required[Literal["inflight_requests", "router_error_rate", "router_latency"]]
    """Required catalogue key for the metric to gate on. `serving_latency` is retired."""

    percentile: int
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    regression_check: Annotated[RegressionCheckParam, PropertyInfo(alias="regressionCheck")]
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

    threshold_check: Annotated[ThresholdCheckParam, PropertyInfo(alias="thresholdCheck")]
    """
    Threshold criteria that fail when the target metric violates the configured
    bound.
    """

    window: str
    """Optional query window for the metric. Defaults to the step soak duration."""
