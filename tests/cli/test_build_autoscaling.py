from __future__ import annotations

import pytest

from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import (
    build_autoscaling,
    normalize_duration,
    build_scaling_rules,
    build_scaling_metrics,
    build_scaling_policies,
)


def test_build_scaling_metrics_utilization() -> None:
    assert build_scaling_metrics(scaling_metric="gpu_utilization", scaling_target=80) == [
        {
            "name": "gpu_utilization",
            "type": "METRIC_TARGET_TYPE_UTILIZATION",
            "target": 80,
        }
    ]


def test_build_scaling_metrics_active_sessions() -> None:
    assert build_scaling_metrics(scaling_metric="active_sessions", scaling_target=25) == [
        {
            "name": "active_sessions",
            "type": "METRIC_TARGET_TYPE_VALUE",
            "target": 25,
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


def test_build_autoscaling_defaults_both_bounds_when_required() -> None:
    autoscaling = build_autoscaling(
        min_replicas=None,
        max_replicas=None,
        scale_up_window=None,
        scale_down_window=None,
        required=True,
    )

    assert autoscaling == {"min_replicas": 1, "max_replicas": 1}


@pytest.mark.parametrize(
    ("min_replicas", "max_replicas", "expected"),
    [
        (0, None, {"min_replicas": 0, "max_replicas": 0}),
        (None, 0, {"min_replicas": 0, "max_replicas": 0}),
        (3, None, {"min_replicas": 3, "max_replicas": 3}),
        (None, 5, {"min_replicas": 1, "max_replicas": 5}),
        (0, 0, {"min_replicas": 0, "max_replicas": 0}),
    ],
)
def test_build_autoscaling_infers_missing_replica_bounds(
    min_replicas: int | None,
    max_replicas: int | None,
    expected: dict[str, int],
) -> None:
    autoscaling = build_autoscaling(
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        scale_up_window=None,
        scale_down_window=None,
        required=True,
    )

    assert autoscaling == expected


@pytest.mark.parametrize(
    ("min_replicas", "max_replicas"),
    [
        (0, 1),
        (1, 0),
        (2, 1),
    ],
)
def test_build_autoscaling_rejects_invalid_explicit_bounds(
    min_replicas: int,
    max_replicas: int,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        build_autoscaling(
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            scale_up_window=None,
            scale_down_window=None,
            required=False,
        )

    output = capsys.readouterr().out
    assert (
        "--min-replicas and --max-replicas must both be 0" in output
        or "cannot be greater than --max-replicas" in output
    )


@pytest.mark.parametrize(
    ("min_replicas", "max_replicas"),
    [
        (0, None),
        (None, 0),
        (0, 1),
        (1, 0),
    ],
)
def test_build_autoscaling_update_requires_explicit_zero_bounds(
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
            required=False,
            infer_replica_defaults=False,
        )

    assert "pass both --min-replicas 0 and --max-replicas 0" in capsys.readouterr().out.replace("\n", " ")


def test_build_autoscaling_update_keeps_partial_nonzero_patch() -> None:
    autoscaling = build_autoscaling(
        min_replicas=3,
        max_replicas=None,
        scale_up_window=None,
        scale_down_window=None,
        required=False,
        infer_replica_defaults=False,
    )

    assert autoscaling == {"min_replicas": 3}


def test_build_autoscaling_accepts_stopped_deployment() -> None:
    autoscaling = build_autoscaling(
        min_replicas=0,
        max_replicas=0,
        scale_up_window=None,
        scale_down_window=None,
        required=True,
    )

    assert autoscaling == {"min_replicas": 0, "max_replicas": 0}


def test_build_autoscaling_includes_scale_to_zero_window() -> None:
    autoscaling = build_autoscaling(
        min_replicas=1,
        max_replicas=2,
        scale_up_window="30s",
        scale_down_window="60s",
        scale_to_zero_window="5m",
        required=True,
    )

    assert autoscaling == {
        "min_replicas": 1,
        "max_replicas": 2,
        "scale_up_window": "30s",
        "scale_down_window": "60s",
        "scale_to_zero_window": "300s",
    }


def test_build_scaling_policies() -> None:
    assert build_scaling_policies(["pods:2:60", "percent:50:300"], option_name="--scale-up-policy") == [
        {
            "type": "SCALING_POLICY_TYPE_PODS",
            "value": 2,
            "period_seconds": 60,
        },
        {
            "type": "SCALING_POLICY_TYPE_PERCENT",
            "value": 50,
            "period_seconds": 300,
        },
    ]


def test_build_scaling_policies_rejects_bad_shape(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_scaling_policies(["pods:2"], option_name="--scale-up-policy")
    assert "KIND:VALUE:PERIOD_SECONDS" in capsys.readouterr().out


def test_build_scaling_rules_maps_selector() -> None:
    assert build_scaling_rules(
        policies=build_scaling_policies(["pods:2:60"], option_name="--scale-up-policy"),
        select_policy="min",
        option_name="--scale-up",
    ) == {
        "policies": [{"type": "SCALING_POLICY_TYPE_PODS", "value": 2, "period_seconds": 60}],
        "select_policy": "SCALING_POLICY_SELECT_MIN",
    }


def test_build_scaling_rules_reset_selector_returns_empty_rules() -> None:
    assert build_scaling_rules(
        policies=None,
        select_policy=None,
        reset_select_policy=True,
        option_name="--scale-up",
    ) == {}


def test_build_scaling_rules_rejects_clear_with_replacement(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        build_scaling_rules(
            policies=build_scaling_policies(["pods:2:60"], option_name="--scale-up-policy"),
            select_policy=None,
            clear_policies=True,
            option_name="--scale-up",
        )
    assert "cannot be combined" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("30s", "30s"),
        ("180s", "180s"),
        ("1.5s", "1.5s"),
        ("1.500s", "1.500s"),
        ("30", "30s"),
        ("10m", "600s"),
        ("2m", "120s"),
        ("1h", "3600s"),
        ("10m30s", "630s"),
        ("5m", "300s"),
        ("1ms", "0.001s"),
        ("-10m", "-600s"),
    ],
)
def test_normalize_duration_accepts_human_and_proto_spellings(raw: str, expected: str) -> None:
    assert normalize_duration(raw, option_name="--interval") == expected


@pytest.mark.parametrize("raw", ["30S", "PT1M", "abc", "", "10m30", "10 x"])
def test_normalize_duration_rejects_invalid_spellings(raw: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        normalize_duration(raw, option_name="--interval")
    output = capsys.readouterr().out
    assert "--interval must be a duration" in output
    assert f"got {raw!r}" in output


def test_build_autoscaling_converts_human_duration_windows() -> None:
    autoscaling = build_autoscaling(
        min_replicas=1,
        max_replicas=1,
        scale_up_window="10m",
        scale_down_window="1h",
        required=True,
    )
    assert autoscaling == {
        "min_replicas": 1,
        "max_replicas": 1,
        "scale_up_window": "600s",
        "scale_down_window": "3600s",
    }
