from __future__ import annotations

import pytest

from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import (
    build_autoscaling,
    build_scaling_metrics,
)


def test_build_scaling_metrics_utilization() -> None:
    assert build_scaling_metrics(scaling_metric="gpu_utilization", scaling_target=80) == [
        {
            "name": "gpu_utilization",
            "type": "METRIC_TARGET_TYPE_UTILIZATION",
            "target": 80,
        }
    ]


def test_build_scaling_metrics_latency_with_percentile() -> None:
    assert build_scaling_metrics(
        scaling_metric="ttft",
        scaling_target=0.5,
        scaling_percentile="p95",
    ) == [
        {
            "name": "ttft",
            "type": "METRIC_TARGET_TYPE_VALUE",
            "target": 0.5,
            "percentile": "p95",
        }
    ]


def test_build_scaling_metrics_none_when_omitted() -> None:
    assert build_scaling_metrics(scaling_metric=None, scaling_target=None) is None


def test_build_scaling_metrics_requires_both(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_scaling_metrics(scaling_metric="gpu_utilization", scaling_target=None)
    assert "--scaling-metric and --scaling-target must be set together" in capsys.readouterr().out


def test_build_scaling_metrics_rejects_percentile_on_utilization(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_scaling_metrics(
            scaling_metric="gpu_utilization",
            scaling_target=80,
            scaling_percentile="p95",
        )
    assert "--scaling-percentile only applies to latency metrics" in capsys.readouterr().out


def test_build_autoscaling_includes_single_metric() -> None:
    autoscaling = build_autoscaling(
        min_replicas=1,
        max_replicas=3,
        scale_up_window=None,
        scale_down_window=None,
        scale_to_zero_window=None,
        scaling_metrics=build_scaling_metrics(scaling_metric="inflight_requests", scaling_target=16),
        required=True,
    )
    assert autoscaling == {
        "min_replicas": 1,
        "max_replicas": 3,
        "scaling_metrics": [
            {
                "name": "inflight_requests",
                "type": "METRIC_TARGET_TYPE_AVERAGE_VALUE",
                "target": 16,
            }
        ],
    }


@pytest.mark.parametrize(
    ("min_replicas", "max_replicas"),
    [
        (0, 1),
        (0, None),
        (1, 0),
        (None, 0),
    ],
)
def test_build_autoscaling_requires_both_replica_bounds_to_stop(
    min_replicas: int | None,
    max_replicas: int | None,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        build_autoscaling(
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            scale_up_window=None,
            scale_down_window=None,
            scale_to_zero_window=None,
            required=False,
        )

    assert "--min-replicas and --max-replicas must both be 0" in capsys.readouterr().out


def test_build_autoscaling_accepts_stopped_deployment() -> None:
    autoscaling = build_autoscaling(
        min_replicas=0,
        max_replicas=0,
        scale_up_window=None,
        scale_down_window=None,
        scale_to_zero_window=None,
        required=True,
    )

    assert autoscaling == {"min_replicas": 0, "max_replicas": 0}
