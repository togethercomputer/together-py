# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from .threshold_check import ThresholdCheck
from .regression_check import RegressionCheck

__all__ = ["MetricRule"]


class MetricRule(BaseModel):
    """Metric gate evaluated during a rollout."""

    name: Literal["inflight_requests", "router_error_rate", "router_latency"]
    """Required catalogue key for the metric to gate on. `serving_latency` is retired."""

    percentile: Optional[int] = None
    """Percentile value, such as 99.

    Set only when stat is METRIC_STAT_TYPE_PERCENTILE.
    """

    regression_check: Optional[RegressionCheck] = FieldInfo(alias="regressionCheck", default=None)
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

    threshold_check: Optional[ThresholdCheck] = FieldInfo(alias="thresholdCheck", default=None)
    """
    Threshold criteria that fail when the target metric violates the configured
    bound.
    """

    window: Optional[str] = None
    """Optional query window for the metric. Defaults to the step soak duration."""
