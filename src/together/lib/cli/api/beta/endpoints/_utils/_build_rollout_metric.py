from __future__ import annotations

from typing import Literal

from together.types.beta.endpoints.rollout_create_params import (
    Metric,
    MetricThresholdCheck,
    MetricRegressionCheck,
)
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import normalize_duration

# Matches Metric.name; serving_latency is retired.
MetricCli = Literal["inflight_requests", "router_error_rate", "router_latency"]
MetricStatCli = Literal["avg", "p50", "p90", "p95", "p99"]
MetricOperatorCli = Literal["gt", "gte", "lt", "lte"]
MetricDirectionCli = Literal["higher-is-worse", "lower-is-worse"]
MetricStatApi = Literal["METRIC_STAT_TYPE_AVG", "METRIC_STAT_TYPE_PERCENTILE"]
MetricOperatorApi = Literal[
    "THRESHOLD_OPERATOR_GT",
    "THRESHOLD_OPERATOR_GTE",
    "THRESHOLD_OPERATOR_LT",
    "THRESHOLD_OPERATOR_LTE",
]
MetricDirectionApi = Literal[
    "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
    "REGRESSION_DIRECTION_LOWER_IS_WORSE",
]

_STAT_MAP: dict[MetricStatCli, tuple[MetricStatApi, int | None]] = {
    "avg": ("METRIC_STAT_TYPE_AVG", None),
    "p50": ("METRIC_STAT_TYPE_PERCENTILE", 50),
    "p90": ("METRIC_STAT_TYPE_PERCENTILE", 90),
    "p95": ("METRIC_STAT_TYPE_PERCENTILE", 95),
    "p99": ("METRIC_STAT_TYPE_PERCENTILE", 99),
}

_OPERATOR_MAP: dict[MetricOperatorCli, MetricOperatorApi] = {
    "gt": "THRESHOLD_OPERATOR_GT",
    "gte": "THRESHOLD_OPERATOR_GTE",
    "lt": "THRESHOLD_OPERATOR_LT",
    "lte": "THRESHOLD_OPERATOR_LTE",
}

_DIRECTION_MAP: dict[MetricDirectionCli, MetricDirectionApi] = {
    "higher-is-worse": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
    "lower-is-worse": "REGRESSION_DIRECTION_LOWER_IS_WORSE",
}

METRIC_STAT_CHOICES = tuple(_STAT_MAP)
METRIC_OPERATOR_CHOICES = tuple(_OPERATOR_MAP)
METRIC_DIRECTION_CHOICES = tuple(_DIRECTION_MAP)


def build_rollout_metrics(
    *,
    metric: MetricCli | None,
    metric_stat: MetricStatCli | None,
    metric_threshold: float | None = None,
    metric_operator: MetricOperatorCli | None = None,
    metric_max_regression: float | None = None,
    metric_direction: MetricDirectionCli | None = None,
    metric_window: str | None = None,
) -> list[Metric] | None:
    """Build a single-element metrics array from simple CLI flags.

    Returns ``None`` when no metric flags are set. Canary-only enforcement belongs
    in the CLI group validator; this helper only validates metric-flag completeness.
    """
    threshold_set = metric_threshold is not None or metric_operator is not None
    regression_set = metric_max_regression is not None or metric_direction is not None
    any_set = (
        metric is not None or metric_stat is not None or threshold_set or regression_set or metric_window is not None
    )
    if not any_set:
        return None

    if metric is None:
        raise ValueError("--metric is required when setting a metric gate.")

    if metric == "router_latency" and metric_stat is None:
        raise ValueError("--metric-stat is required for --metric router_latency (avg, p50, p90, p95, or p99).")

    if threshold_set and regression_set:
        raise ValueError(
            "Use either a threshold gate (--metric-threshold/--metric-operator) "
            "or a regression gate (--metric-max-regression/--metric-direction), not both."
        )
    if not threshold_set and not regression_set:
        raise ValueError(
            "A metric gate requires either --metric-operator (optional --metric-threshold) "
            "or --metric-direction (optional --metric-max-regression)."
        )

    payload: Metric = {"name": metric}
    if metric_stat is not None:
        if metric_stat not in _STAT_MAP:
            known = ", ".join(METRIC_STAT_CHOICES)
            raise ValueError(f"Unknown --metric-stat {metric_stat!r}. Choose one of: {known}.")
        stat, percentile = _STAT_MAP[metric_stat]
        payload["stat"] = stat
        if percentile is not None:
            payload["percentile"] = percentile

    if threshold_set:
        if metric_operator is None:
            raise ValueError("--metric-operator is required for a threshold gate.")
        if metric_operator not in _OPERATOR_MAP:
            known = ", ".join(METRIC_OPERATOR_CHOICES)
            raise ValueError(f"Unknown --metric-operator {metric_operator!r}. Choose one of: {known}.")
        threshold_check: MetricThresholdCheck = {"operator": _OPERATOR_MAP[metric_operator]}
        if metric_threshold is not None:
            threshold_check["value"] = metric_threshold
        payload["threshold_check"] = threshold_check
    else:
        if metric_direction is None:
            raise ValueError("--metric-direction is required for a regression gate.")
        if metric_direction not in _DIRECTION_MAP:
            known = ", ".join(METRIC_DIRECTION_CHOICES)
            raise ValueError(f"Unknown --metric-direction {metric_direction!r}. Choose one of: {known}.")
        regression_check: MetricRegressionCheck = {"direction": _DIRECTION_MAP[metric_direction]}
        if metric_max_regression is not None:
            regression_check["max_regression_percent"] = metric_max_regression
        payload["regression_check"] = regression_check

    if metric_window is not None:
        payload["window"] = normalize_duration(metric_window, option_name="--metric-window")

    return [payload]
