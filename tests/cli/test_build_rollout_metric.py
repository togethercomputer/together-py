from __future__ import annotations

import pytest

from together.lib.cli.api.beta.endpoints._utils._build_rollout_metric import build_rollout_metrics


def test_none_when_omitted() -> None:
    assert (
        build_rollout_metrics(
            metric=None,
            metric_stat=None,
        )
        is None
    )


def test_converts_human_metric_window() -> None:
    assert build_rollout_metrics(
        metric="router_error_rate",
        metric_stat="avg",
        metric_threshold=0.5,
        metric_operator="lte",
        metric_window="5m",
    ) == [
        {
            "name": "router_error_rate",
            "stat": "METRIC_STAT_TYPE_AVG",
            "threshold_check": {
                "operator": "THRESHOLD_OPERATOR_LTE",
                "value": 0.5,
            },
            "window": "300s",
        }
    ]


def test_rejects_unparseable_metric_window(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_rollout_metrics(
            metric="router_error_rate",
            metric_stat="avg",
            metric_threshold=0.5,
            metric_operator="lte",
            metric_window="PT1M",
        )
    assert "--metric-window must be a duration" in capsys.readouterr().out


def test_threshold_gate_with_percentile() -> None:
    assert build_rollout_metrics(
        metric="router_latency",
        metric_stat="p99",
        metric_threshold=500,
        metric_operator="lte",
        metric_window="60s",
    ) == [
        {
            "name": "router_latency",
            "stat": "METRIC_STAT_TYPE_PERCENTILE",
            "percentile": 99,
            "threshold_check": {
                "operator": "THRESHOLD_OPERATOR_LTE",
                "value": 500,
            },
            "window": "60s",
        }
    ]


def test_regression_gate_with_avg() -> None:
    assert build_rollout_metrics(
        metric="router_error_rate",
        metric_stat="avg",
        metric_max_regression=10,
        metric_direction="higher-is-worse",
    ) == [
        {
            "name": "router_error_rate",
            "stat": "METRIC_STAT_TYPE_AVG",
            "regression_check": {
                "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
                "max_regression_percent": 10,
            },
        }
    ]


def test_requires_metric() -> None:
    with pytest.raises(ValueError, match="--metric is required"):
        build_rollout_metrics(
            metric=None,
            metric_stat="avg",
            metric_threshold=500,
            metric_operator="lte",
        )


def test_requires_stat_for_router_latency() -> None:
    with pytest.raises(ValueError, match="--metric-stat is required for --metric router_latency"):
        build_rollout_metrics(
            metric="router_latency",
            metric_stat=None,
            metric_threshold=500,
            metric_operator="lte",
        )


def test_omits_stat_for_error_rate() -> None:
    assert build_rollout_metrics(
        metric="router_error_rate",
        metric_stat=None,
        metric_operator="lte",
        metric_threshold=0.01,
    ) == [
        {
            "name": "router_error_rate",
            "threshold_check": {
                "operator": "THRESHOLD_OPERATOR_LTE",
                "value": 0.01,
            },
        }
    ]


def test_omits_threshold_value_when_operator_only() -> None:
    assert build_rollout_metrics(
        metric="inflight_requests",
        metric_stat=None,
        metric_operator="lte",
    ) == [
        {
            "name": "inflight_requests",
            "threshold_check": {
                "operator": "THRESHOLD_OPERATOR_LTE",
            },
        }
    ]


def test_omits_max_regression_when_direction_only() -> None:
    assert build_rollout_metrics(
        metric="router_error_rate",
        metric_stat=None,
        metric_direction="higher-is-worse",
    ) == [
        {
            "name": "router_error_rate",
            "regression_check": {
                "direction": "REGRESSION_DIRECTION_HIGHER_IS_WORSE",
            },
        }
    ]


def test_requires_check_type() -> None:
    with pytest.raises(ValueError, match="requires either --metric-operator"):
        build_rollout_metrics(
            metric="router_latency",
            metric_stat="p99",
        )


def test_rejects_both_check_types() -> None:
    with pytest.raises(ValueError, match="not both"):
        build_rollout_metrics(
            metric="router_latency",
            metric_stat="p99",
            metric_threshold=500,
            metric_operator="lte",
            metric_max_regression=10,
            metric_direction="higher-is-worse",
        )


def test_threshold_operator_required() -> None:
    with pytest.raises(ValueError, match="--metric-operator is required"):
        build_rollout_metrics(
            metric="router_latency",
            metric_stat="p99",
            metric_threshold=500,
            metric_operator=None,
        )


def test_regression_direction_required() -> None:
    with pytest.raises(ValueError, match="--metric-direction is required"):
        build_rollout_metrics(
            metric="router_latency",
            metric_stat="p99",
            metric_max_regression=10,
            metric_direction=None,
        )
