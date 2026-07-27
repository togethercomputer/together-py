from __future__ import annotations

import re
import sys
from typing import Literal, cast, overload

from together.types.beta import DeploymentAutoscalingParam
from together.lib.cli.utils._console import console
from together.types.beta.deployment_autoscaling_param import ScalingMetric

# OpenAPI DE.Autoscaling windows: protobuf Duration JSON, seconds only (e.g. "30s").
_DURATION_RE = re.compile(r"^-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,9})?s$")
_BARE_SECONDS_RE = re.compile(r"^-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,9})?$")

MetricType = Literal[
    "METRIC_TARGET_TYPE_VALUE",
    "METRIC_TARGET_TYPE_UTILIZATION",
    "METRIC_TARGET_TYPE_AVERAGE_VALUE",
]

ScalingMetricName = Literal[
    "inflight_requests",
    "gpu_utilization",
    "token_utilization",
    "cache_hit_rate",
    "throughput_per_replica",
    "ttft",
    "decoding_speed",
    "e2e_latency",
]

ScalingPercentile = Literal["p50", "p90", "p95", "p99"]

# Fixed type per metric name (see examples/internal-team-guides/autoscaling.md).
_METRIC_TYPES: dict[ScalingMetricName, MetricType] = {
    "inflight_requests": "METRIC_TARGET_TYPE_AVERAGE_VALUE",
    "gpu_utilization": "METRIC_TARGET_TYPE_UTILIZATION",
    "token_utilization": "METRIC_TARGET_TYPE_UTILIZATION",
    "cache_hit_rate": "METRIC_TARGET_TYPE_UTILIZATION",
    "throughput_per_replica": "METRIC_TARGET_TYPE_AVERAGE_VALUE",
    "ttft": "METRIC_TARGET_TYPE_VALUE",
    "decoding_speed": "METRIC_TARGET_TYPE_VALUE",
    "e2e_latency": "METRIC_TARGET_TYPE_VALUE",
}

_VALID_PERCENTILES: frozenset[ScalingPercentile] = frozenset({"p50", "p90", "p95", "p99"})
SCALING_METRIC_NAMES = tuple(_METRIC_TYPES)


def normalize_duration(value: str | None, *, option_name: str) -> str | None:
    """Accept bare seconds (`30`) or Duration JSON (`30s`); reject other units."""
    if value is None:
        return None
    value = value.strip()
    if _DURATION_RE.match(value):
        return value
    if _BARE_SECONDS_RE.match(value):
        return f"{value}s"
    console.print(f"Error: {option_name} must be a duration in seconds, e.g. 30 or 30s (got {value!r}).")
    sys.exit(1)


def build_scaling_metrics(
    *,
    scaling_metric: ScalingMetricName | None,
    scaling_target: float | None,
    scaling_percentile: ScalingPercentile | None = None,
) -> list[ScalingMetric] | None:
    """Build a single-element scalingMetrics array from simple CLI flags."""
    if scaling_metric is None and scaling_target is None and scaling_percentile is None:
        return None

    if scaling_metric is None or scaling_target is None:
        console.print("Error: --scaling-metric and --scaling-target must be set together.")
        sys.exit(1)

    metric_type = _METRIC_TYPES.get(scaling_metric)
    if metric_type is None:
        known = ", ".join(SCALING_METRIC_NAMES)
        console.print(f"Error: unknown --scaling-metric {scaling_metric!r}. Choose one of: {known}.")
        sys.exit(1)

    metric: ScalingMetric = {
        "name": scaling_metric,
        "type": metric_type,
        "target": scaling_target,
    }

    if scaling_percentile is not None:
        if scaling_percentile not in _VALID_PERCENTILES:
            console.print(
                f"Error: --scaling-percentile must be one of {', '.join(sorted(_VALID_PERCENTILES))} "
                f"(got {scaling_percentile!r})."
            )
            sys.exit(1)
        if metric_type != "METRIC_TARGET_TYPE_VALUE":
            console.print(
                f"Error: --scaling-percentile only applies to latency metrics "
                f"(ttft, e2e_latency, decoding_speed), not {scaling_metric!r}."
            )
            sys.exit(1)
        metric["percentile"] = scaling_percentile

    return [metric]


@overload
def build_autoscaling(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scale_to_zero_window: str | None,
    scaling_metrics: list[ScalingMetric] | None = ...,
    required: Literal[True],
    infer_replica_defaults: bool = ...,
) -> DeploymentAutoscalingParam: ...


@overload
def build_autoscaling(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scale_to_zero_window: str | None,
    scaling_metrics: list[ScalingMetric] | None = ...,
    required: Literal[False],
    infer_replica_defaults: bool = ...,
) -> DeploymentAutoscalingParam | None: ...


def build_autoscaling(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scale_to_zero_window: str | None,
    scaling_metrics: list[ScalingMetric] | None = None,
    required: bool = False,
    infer_replica_defaults: bool = True,
) -> DeploymentAutoscalingParam | None:
    if infer_replica_defaults:
        if min_replicas is None and max_replicas is None and required:
            min_replicas, max_replicas = 1, 1
        elif min_replicas is not None and max_replicas is None:
            # Stopped (0) or fixed-size (N): mirror the only bound the user set.
            max_replicas = min_replicas
        elif max_replicas == 0 and min_replicas is None:
            min_replicas = 0
        elif max_replicas is not None and min_replicas is None and required:
            # Create/deploy with only --max-replicas N (N > 0): keep the usual min of 1.
            min_replicas = 1
    elif (min_replicas == 0 or max_replicas == 0) and not (min_replicas == 0 and max_replicas == 0):
        # Updates are patchy: don't invent the other bound when stopping.
        console.print("Error: to stop a deployment, pass both --min-replicas 0 and --max-replicas 0.")
        sys.exit(1)

    if min_replicas is not None and max_replicas is not None and (min_replicas == 0) != (max_replicas == 0):
        console.print(
            "Error: --min-replicas and --max-replicas must both be 0 to stop a deployment. "
            "Pass --min-replicas 0 --max-replicas 0."
        )
        sys.exit(1)

    if min_replicas is not None and max_replicas is not None and min_replicas > max_replicas:
        console.print(f"Error: --min-replicas ({min_replicas}) cannot be greater than --max-replicas ({max_replicas})")
        sys.exit(1)

    autoscaling = {
        key: value
        for key, value in {
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "scale_up_window": normalize_duration(scale_up_window, option_name="--scale-up-window"),
            "scale_down_window": normalize_duration(scale_down_window, option_name="--scale-down-window"),
            "scale_to_zero_window": normalize_duration(scale_to_zero_window, option_name="--scale-to-zero-window"),
            "scaling_metrics": scaling_metrics,
        }.items()
        if value is not None
    }
    if not autoscaling:
        if not required:
            return None
        console.print("Error: deployment create requires autoscaling. Pass --min-replicas and/or --max-replicas.")
        sys.exit(1)
    return cast(DeploymentAutoscalingParam, autoscaling)
