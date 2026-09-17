from __future__ import annotations

import re
from typing import Literal, cast, overload

from together.types.beta import DeploymentAutoscalingParam, ScalingMetricParam
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils._console import console

# Wire format is protobuf Duration JSON, seconds only (e.g. "30s", "600s").
# CLI also accepts bare seconds (`30`) and Go-style units (`10m`, `1h`, `10m30s`).
_DURATION_RE = re.compile(r"^-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,9})?s$")
_BARE_SECONDS_RE = re.compile(r"^-?(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,9})?$")
_HUMAN_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)(ns|us|µs|μs|ms|h|m|s)")
_UNIT_NANOS: dict[str, int] = {
    "ns": 1,
    "us": 1_000,
    "µs": 1_000,
    "μs": 1_000,
    "ms": 1_000_000,
    "s": 1_000_000_000,
    "m": 60_000_000_000,
    "h": 3_600_000_000_000,
}

MetricType = Literal[
    "METRIC_TARGET_TYPE_VALUE",
    "METRIC_TARGET_TYPE_UTILIZATION",
    "METRIC_TARGET_TYPE_AVERAGE_VALUE",
]

ScalingMetricName = Literal[
    "active_sessions",
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
    "active_sessions": "METRIC_TARGET_TYPE_VALUE",
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


def _token_to_nanos(amount: str, unit: str) -> int:
    unit_nanos = _UNIT_NANOS[unit]
    if "." not in amount:
        return int(amount) * unit_nanos
    whole, frac = amount.split(".", 1)
    whole_i = int(whole) if whole else 0
    scale = int(10 ** len(frac))
    return whole_i * unit_nanos + (int(frac) * unit_nanos) // scale


def _format_proto_duration(nanos: int) -> str:
    sign = "-" if nanos < 0 else ""
    nanos = abs(nanos)
    secs, rem = divmod(nanos, 1_000_000_000)
    if rem == 0:
        return f"{sign}{secs}s"
    return f"{sign}{secs}.{rem:09d}".rstrip("0") + "s"


def _human_duration_to_proto(value: str) -> str | None:
    sign = -1 if value.startswith("-") else 1
    if value.startswith("-") or value.startswith("+"):
        value = value[1:]
    if not value:
        return None
    total = 0
    pos = 0
    while pos < len(value):
        match = _HUMAN_TOKEN_RE.match(value, pos)
        if match is None:
            return None
        total += _token_to_nanos(match.group(1), match.group(2))
        pos = match.end()
    return _format_proto_duration(sign * total)


@overload
def normalize_duration(value: None, *, option_name: str) -> None: ...


@overload
def normalize_duration(value: str, *, option_name: str) -> str: ...


def normalize_duration(value: str | None, *, option_name: str) -> str | None:
    """Normalize a CLI duration to protobuf Duration JSON (`600s`).

    Accepts Duration JSON (`30s`), bare seconds (`30`), and Go-style units
    (`10m`, `1h`, `10m30s`). Other spellings exit with a named error.
    """
    if value is None:
        return None
    value = value.strip()
    if _DURATION_RE.match(value):
        return value
    if _BARE_SECONDS_RE.match(value):
        return f"{value}s"
    converted = _human_duration_to_proto(value)
    if converted is not None and _DURATION_RE.match(converted):
        return converted
    console.print(f"Error: {option_name} must be a duration, e.g. 30, 30s, 10m, or 1h (got {value!r}).")
    raise CliDiagnosticExit(f"Invalid duration for {option_name}")


def build_scaling_metrics(
    *,
    scaling_metric: ScalingMetricName | None,
    scaling_target: float | None,
    scaling_percentile: ScalingPercentile | None = None,
) -> list[ScalingMetricParam] | None:
    """Build a single-element scalingMetrics array from simple CLI flags."""
    if scaling_metric is None and scaling_target is None and scaling_percentile is None:
        return None

    if scaling_metric is None or scaling_target is None:
        console.print("Error: --scaling-metric and --scaling-target must be set together.")
        raise CliDiagnosticExit("Autoscaling metric and target must be set together")

    metric_type = _METRIC_TYPES.get(scaling_metric)
    if metric_type is None:
        known = ", ".join(SCALING_METRIC_NAMES)
        console.print(f"Error: unknown --scaling-metric {scaling_metric!r}. Choose one of: {known}.")
        raise CliDiagnosticExit("Unknown autoscaling metric")

    metric: ScalingMetricParam = {
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
            raise CliDiagnosticExit("Invalid autoscaling percentile")
        if metric_type != "METRIC_TARGET_TYPE_VALUE":
            console.print(
                f"Error: --scaling-percentile only applies to latency metrics "
                f"(ttft, e2e_latency, decoding_speed), not {scaling_metric!r}."
            )
            raise CliDiagnosticExit("Autoscaling percentile requires a latency metric")
        metric["percentile"] = scaling_percentile

    return [metric]


@overload
def build_autoscaling(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scaling_metrics: list[ScalingMetricParam] | None = ...,
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
    scaling_metrics: list[ScalingMetricParam] | None = ...,
    required: Literal[False],
    infer_replica_defaults: bool = ...,
) -> DeploymentAutoscalingParam | None: ...


def build_autoscaling(
    *,
    min_replicas: int | None,
    max_replicas: int | None,
    scale_up_window: str | None,
    scale_down_window: str | None,
    scaling_metrics: list[ScalingMetricParam] | None = None,
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
        raise CliDiagnosticExit("Scaling to zero requires both replica bounds")

    if min_replicas is not None and max_replicas is not None and (min_replicas == 0) != (max_replicas == 0):
        console.print(
            "Error: --min-replicas and --max-replicas must both be 0 to stop a deployment. "
            "Pass --min-replicas 0 --max-replicas 0."
        )
        raise CliDiagnosticExit("Scaling to zero requires both replica bounds")

    if min_replicas is not None and max_replicas is not None and min_replicas > max_replicas:
        console.print(f"Error: --min-replicas ({min_replicas}) cannot be greater than --max-replicas ({max_replicas})")
        raise CliDiagnosticExit("Autoscaling minimum replicas cannot exceed maximum replicas")

    autoscaling = {
        key: value
        for key, value in {
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "scale_up_window": normalize_duration(scale_up_window, option_name="--scale-up-window"),
            "scale_down_window": normalize_duration(scale_down_window, option_name="--scale-down-window"),
            "scaling_metrics": scaling_metrics,
        }.items()
        if value is not None
    }
    if not autoscaling:
        if not required:
            return None
        console.print("Error: deployment create requires autoscaling. Pass --min-replicas and/or --max-replicas.")
        raise CliDiagnosticExit("Deployment creation requires autoscaling")
    return cast(DeploymentAutoscalingParam, autoscaling)
