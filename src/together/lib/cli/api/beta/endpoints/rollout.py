from __future__ import annotations

from typing import Any, Optional
from typing_extensions import Annotated

from cyclopts import Group, Parameter
from rich.markup import escape as escape_rich_markup
from cyclopts.argument import ArgumentCollection
from cyclopts.validators import Number, mutually_exclusive

from together import AsyncClient, omit
from together._utils._json import openapi_dumps
from together.types.beta.endpoint import Endpoint
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console, error_console
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.endpoints.rollout import Rollout
from together.lib.cli.api.beta.endpoints.retrieve import retrieve
from together.types.beta.endpoints.rollout_create_params import Canary, Rolling, BlueGreen
from together.lib.cli.api.beta.endpoints._utils._rollouts import (
    fallback_active_rollout_from_list,
    resolve_rollout_by_id,
)
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_endpoint
from together.lib.cli.api.beta.endpoints._utils._build_autoscaling import normalize_duration
from together.lib.cli.api.beta.endpoints._utils._build_rollout_metric import (
    MetricCli,
    MetricStatCli,
    MetricOperatorCli,
    MetricDirectionCli,
    build_rollout_metrics,
)
from together.lib.cli.api.beta.endpoints._utils._detach_from_experiments import (
    detach_deployment_from_experiments,
)
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import (
    AmbiguousDeploymentError,
    resolve_deployment_id,
    resolve_deployment_ids,
)


class NoActiveRolloutError(ValueError):
    """Raised when an endpoint/deployment has no controllable active rollout."""


_CONTROL_PARAMS = frozenset({"cancel", "pause", "resume", "promote"})
_METRIC_PARAMS = frozenset(
    {
        "metric",
        "metric_stat",
        "metric_threshold",
        "metric_operator",
        "metric_max_regression",
        "metric_direction",
        "metric_window",
    }
)
_CREATE_PARAMS = frozenset(
    {
        "source",
        "canary",
        "blue_green",
        "rolling",
        "steps",
        "interval",
        "final_source_replicas",
        "final_target_replicas",
        "detach",
        *_METRIC_PARAMS,
    }
)
_REASON_PARAMS = frozenset({"cancel", "pause"})
_CANARY_ONLY_PARAMS = frozenset({"steps", "interval"}) | _METRIC_PARAMS


def _populated_names(argument_collection: ArgumentCollection) -> set[str]:
    return {argument.field_info.name for argument in argument_collection.filter_by(value_set=True)}


def _control_mode_validator(argument_collection: ArgumentCollection) -> None:
    """Controls are exclusive with create/strategy options; --reason only with --cancel/--pause."""
    populated = _populated_names(argument_collection)
    controls = populated & _CONTROL_PARAMS
    creates = populated & _CREATE_PARAMS
    if controls and creates:
        raise ValueError("Strategy and create options cannot be combined with rollout control flags.")
    if "reason" in populated and not (populated & _REASON_PARAMS):
        raise ValueError("--reason is only valid with --cancel or --pause.")


def _canary_options_validator(argument_collection: ArgumentCollection) -> None:
    """--steps/--interval/--metric* require --canary."""
    populated = _populated_names(argument_collection)
    if populated & _CANARY_ONLY_PARAMS and "canary" not in populated:
        raise ValueError("--steps, --interval, and --metric* require --canary.")


# Display-only — do not put a mutually_exclusive validator here; --reason must
# combine with --cancel/--pause (enforced by ModeGroup / _control_mode_validator).
ControlDisplayGroup = Group(
    "Rollout Controls",
    help="These flags can be used on an active rollout to modify its state.",
    sort_key=4,
    default_parameter=Parameter(negative=(), show_default=False),
)
# Exclusive among control actions only (--cancel/--pause/--resume/--promote).
ControlGroup = Group(
    validator=mutually_exclusive,
    default_parameter=Parameter(negative=(), show_default=False),
)
StrategyGroup = Group(
    validator=mutually_exclusive,
    default_parameter=Parameter(negative=(), show_default=False),
)
# Anonymous: control vs create exclusivity + --reason only with --cancel/--pause
ModeGroup = Group(validator=_control_mode_validator)

CanaryGroup = Group(
    "Canary Rollout",
    help=(
        "Use [primary]`--canary`[/primary] to create a canary rollout. "
        "Optional [primary]`--metric*`[/primary] flags configure a single metric gate."
    ),
    validator=_canary_options_validator,
    sort_key=1,
)
BlueGreenGroup = Group(
    "Blue/Green Rollout",
    help="Use [primary]`--blue-green`[/primary] for a single cutover.",
    sort_key=2,
)
RollingGroup = Group(
    "Rolling Rollout",
    help="Use [primary]`--rolling`[/primary] for a capacity-preserving batch swap.",
    sort_key=3,
)


async def rollout(
    id: Annotated[
        str,
        Parameter(
            help=(
                """Different usages can take different forms of identifiers.

When creating a new rollout, the following forms are accepted:
  - Deployment ID
  - Deployment name

When using control flags (--cancel/--pause/--resume/--promote) to change the state of an existing rollout, the following forms are accepted:
  - Endpoint ID (preferred)
  - Endpoint name
  - Deployment ID
  - Deployment name
  - Rollout ID

Note: If a deployment name is ambiguous, pass the ID."""
            )
        ),
    ],
    *,
    source: Annotated[
        Optional[str],
        Parameter(
            name="--source",
            help="""Active deployment ID or name to replace.

When omitted, infers the sole other deployment with traffic weight > 0.""",
            group=ModeGroup,
        ),
    ] = None,
    cancel: Annotated[
        bool,
        Parameter(
            name="--cancel",
            help="Cancel an in-progress rollout, Endpoint and deployments will be left in the current traffic split",
            group=(ControlDisplayGroup, ControlGroup, ModeGroup),
        ),
    ] = False,
    pause: Annotated[
        bool,
        Parameter(
            name="--pause",
            help="Pause an in-progress rollout at the current traffic split. Can be resumed later",
            group=(ControlDisplayGroup, ControlGroup, ModeGroup),
        ),
    ] = False,
    resume: Annotated[
        bool,
        Parameter(
            name="--resume",
            help="Resume a paused rollout from its current step",
            group=(ControlDisplayGroup, ControlGroup, ModeGroup),
        ),
    ] = False,
    promote: Annotated[
        bool,
        Parameter(
            name="--promote",
            help="Complete a rollout by immediately shifting 100% traffic to the target",
            group=(ControlDisplayGroup, ControlGroup, ModeGroup),
        ),
    ] = False,
    reason: Annotated[
        Optional[str],
        Parameter(
            name="--reason",
            help=("User-provided auditing reason for a cancel or pause action."),
            group=(ControlDisplayGroup, ModeGroup),
        ),
    ] = None,
    blue_green: Annotated[
        bool,
        Parameter(
            name="--blue-green",
            help="Blue-green strategy (single cutover).",
            group=(StrategyGroup, BlueGreenGroup, ModeGroup),
        ),
    ] = False,
    rolling: Annotated[
        bool,
        Parameter(
            name="--rolling",
            help="Rolling strategy (capacity-preserving batch swap)",
            group=(StrategyGroup, RollingGroup, ModeGroup),
        ),
    ] = False,
    canary: Annotated[
        bool,
        Parameter(
            name="--canary",
            help="Gradual canary rollout. Omitting --steps/--interval uses server defaults.",
            group=(StrategyGroup, CanaryGroup, ModeGroup),
        ),
    ] = False,
    steps: Annotated[
        Optional[str],
        Parameter(
            name="--steps",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Comma-separated canary traffic percents, e.g. 10,50,100. "
                "Only valid with --canary. Final step must be 100. "
                "Omit to use the server default ladder."
            ),
        ),
    ] = None,
    interval: Annotated[
        Optional[str],
        Parameter(
            name="--interval",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Wait between canary steps, e.g. 30s or 10m. Only valid with --canary. Omit to use the server default."
            ),
        ),
    ] = None,
    metric: Annotated[
        Optional[MetricCli],
        Parameter(
            name="--metric",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Metric name for a canary gate: inflight_requests, router_error_rate, or router_latency. "
                "Must be set with a threshold (--metric-operator) or regression (--metric-direction) check. "
                "--metric-stat is required for router_latency. Only valid with --canary. CLI supports one metric gate."
            ),
        ),
    ] = None,
    metric_stat: Annotated[
        Optional[MetricStatCli],
        Parameter(
            name="--metric-stat",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Aggregation for --metric. Choices: avg, p50, p90, p95, p99. "
                "Optional for router_error_rate and inflight_requests (server default: avg). "
                "Required for router_latency (avg or a percentile). "
                "Percentile choices set stat=PERCENTILE automatically."
            ),
        ),
    ] = None,
    metric_threshold: Annotated[
        Optional[float],
        Parameter(
            name="--metric-threshold",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Absolute threshold value for the target metric. "
                "Optional with --metric-operator; omitted is 0 (strictest). "
                "router_error_rate is a ratio in [0, 1], router_latency is milliseconds, "
                "inflight_requests is in-flight requests per ready replica. "
                "Mutually exclusive with regression flags."
            ),
        ),
    ] = None,
    metric_operator: Annotated[
        Optional[MetricOperatorCli],
        Parameter(
            name="--metric-operator",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Comparison operator for a threshold gate. Choices: gt, gte, lt, lte. "
                "Required for a threshold gate. Optional --metric-threshold defaults to 0."
            ),
        ),
    ] = None,
    metric_max_regression: Annotated[
        Optional[float],
        Parameter(
            name="--metric-max-regression",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Max allowed regression percent vs the source. "
                "Optional with --metric-direction; omitted is 0 (any regression fails). "
                "Mutually exclusive with threshold flags."
            ),
            validator=Number(gte=0),
        ),
    ] = None,
    metric_direction: Annotated[
        Optional[MetricDirectionCli],
        Parameter(
            name="--metric-direction",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Which direction counts as regression. Choices: higher-is-worse, lower-is-worse. "
                "Required for a regression gate. Optional --metric-max-regression defaults to 0."
            ),
        ),
    ] = None,
    metric_window: Annotated[
        Optional[str],
        Parameter(
            name="--metric-window",
            group=(CanaryGroup, ModeGroup),
            help=(
                "Optional query window for the metric gate, e.g. 60s or 5m. "
                "Defaults to the step soak duration when omitted."
            ),
        ),
    ] = None,
    final_source_replicas: Annotated[
        Optional[int],
        Parameter(
            name="--final-source-replicas",
            group=ModeGroup,
            help=(
                "Final replica count for the source deployment after rollout. "
                "Must be >= 0. Omit to default to 0 (drain and stop the source)."
            ),
            validator=Number(gte=0),
        ),
    ] = None,
    final_target_replicas: Annotated[
        Optional[int],
        Parameter(
            name="--final-target-replicas",
            group=ModeGroup,
            help=(
                "Target replica floor at completion. Must be >= 1. "
                "Omit to default to the source replica count, or source+target combined after a cancel. "
                "The target autoscaling max may be lifted to the landing ceiling."
            ),
            validator=Number(gte=1),
        ),
    ] = None,
    detach: Annotated[
        bool,
        Parameter(
            name="--detach",
            help="Detach the deployment from any associated shadow or a/b experiment groups",
            negative=(),
            show_default=False,
            group=ModeGroup,
        ),
    ] = False,
    config: CLIConfigParameter,
) -> None:
    """Roll out a deployment, or control an existing rollout."""
    actions: list[str] = []

    if cancel or pause or resume or promote:
        result, message = await _control_rollout(
            id,
            cancel=cancel,
            pause=pause,
            resume=resume,
            promote=promote,
            reason=reason,
            config=config,
        )
    else:
        result, actions = await _create_and_start_rollout(
            target_deployment_id=id,
            source_deployment_id=source,
            canary=canary,
            blue_green=blue_green,
            rolling=rolling,
            steps=steps,
            interval=interval,
            metric=metric,
            metric_stat=metric_stat,
            metric_threshold=metric_threshold,
            metric_operator=metric_operator,
            metric_max_regression=metric_max_regression,
            metric_direction=metric_direction,
            metric_window=metric_window,
            final_source_replicas=final_source_replicas,
            final_target_replicas=final_target_replicas,
            detach=detach,
            config=config,
        )
        message = "Rollout started."

    if config.json:
        payload: dict[str, Any] = {"rollout": result}
        if actions:
            payload["actions"] = actions
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    if actions:
        console.print(f"[dim]{'; '.join(actions)}[/dim]")
    console.print(f"[green]√[/green] {message}")

    # Print the endpoint details
    await retrieve(result.endpoint_id, config=config)


async def _control_rollout(
    ref: str,
    *,
    cancel: bool,
    pause: bool,
    resume: bool,
    promote: bool,
    reason: str | None,
    config: CLIConfigParameter,
) -> tuple[Rollout, str]:
    existing_rollout = await _resolve_active_rollout(config, ref)
    rollout_id = existing_rollout.id

    if cancel:
        rollout = await show_loading_status(
            "Cancelling rollout...",
            config.client.beta.endpoints.rollouts.cancel(
                id=rollout_id,
                endpoint_id=existing_rollout.endpoint_id,
                reason=reason or "Cancelled via tg beta endpoints rollout --cancel",
                etag=existing_rollout.etag or omit,
            ),
        )
        return rollout, "Rollout cancelled (traffic frozen at current split)."

    if pause:
        rollout = await show_loading_status(
            "Pausing rollout...",
            config.client.beta.endpoints.rollouts.pause(
                id=rollout_id,
                endpoint_id=existing_rollout.endpoint_id,
                reason=reason or "Paused via tg beta endpoints rollout --pause",
                etag=existing_rollout.etag or omit,
            ),
        )
        return rollout, "Rollout paused."

    if resume:
        rollout = await show_loading_status(
            "Resuming rollout...",
            config.client.beta.endpoints.rollouts.resume(
                id=rollout_id,
                endpoint_id=existing_rollout.endpoint_id,
                etag=existing_rollout.etag or omit,
            ),
        )
        return rollout, "Rollout resumed."

    if not promote:
        raise AssertionError("expected a control flag")

    rollout = await show_loading_status(
        "Promoting rollout...",
        config.client.beta.endpoints.rollouts.promote(
            id=rollout_id,
            endpoint_id=existing_rollout.endpoint_id,
            etag=existing_rollout.etag or omit,
        ),
    )
    return rollout, "Rollout promoted (100% traffic on target)."


async def _create_and_start_rollout(
    *,
    target_deployment_id: str,
    source_deployment_id: str | None,
    canary: bool,
    blue_green: bool,
    rolling: bool,
    steps: str | None,
    interval: str | None,
    metric: MetricCli | None,
    metric_stat: MetricStatCli | None,
    metric_threshold: float | None,
    metric_operator: MetricOperatorCli | None,
    metric_max_regression: float | None,
    metric_direction: MetricDirectionCli | None,
    metric_window: str | None,
    final_source_replicas: int | None,
    final_target_replicas: int | None,
    detach: bool,
    config: CLIConfigParameter,
) -> tuple[Rollout, list[str]]:
    # Validate strategy / metric gate before any network I/O or destructive detach work.
    canary_payload, blue_green_payload, rolling_payload = resolve_rollout_strategy(
        canary=canary,
        blue_green=blue_green,
        rolling=rolling,
        steps=steps,
        interval=interval,
    )
    metrics_payload = build_rollout_metrics(
        metric=metric,
        metric_stat=metric_stat,
        metric_threshold=metric_threshold,
        metric_operator=metric_operator,
        metric_max_regression=metric_max_regression,
        metric_direction=metric_direction,
        metric_window=metric_window,
    )

    if source_deployment_id is not None:
        (endpoint, target_id), (source_endpoint, source_id) = await resolve_deployment_ids(
            config.client,
            target_deployment_id,
            source_deployment_id,
        )
        if source_endpoint.id != endpoint.id:
            raise ValueError(
                f"Source deployment {source_id} is on endpoint {source_endpoint.id}, "
                f"but target deployment {target_id} is on endpoint {endpoint.id}."
            )
    else:
        endpoint, target_id = await resolve_deployment_id(config.client, target_deployment_id)
        source_id = _infer_active_source(endpoint, target_id=target_id)
    _verify_rollout_pair(endpoint, source_id=source_id, target_id=target_id)

    actions: list[str] = []
    if detach:
        actions = await detach_deployment_from_experiments(
            config,
            endpoint=endpoint,
            deployment_id=target_id,
        )

    created_rollout_id: str | None = None
    try:
        rollout = await show_loading_status(
            "Creating rollout...",
            config.client.beta.endpoints.rollouts.create(
                endpoint_id=endpoint.id,
                source_deployment_id=source_id,
                target_deployment_id=target_id,
                canary=canary_payload if canary_payload is not None else omit,
                blue_green=blue_green_payload if blue_green_payload is not None else omit,
                rolling=rolling_payload if rolling_payload is not None else omit,
                metrics=metrics_payload if metrics_payload is not None else omit,
                final_source_replicas=final_source_replicas if final_source_replicas is not None else omit,
                final_target_replicas=final_target_replicas if final_target_replicas is not None else omit,
            ),
        )
        created_rollout_id = rollout.id

        rollout = await show_loading_status(
            "Starting rollout...",
            config.client.beta.endpoints.rollouts.start(
                id=rollout.id,
                endpoint_id=endpoint.id,
            ),
        )
    except Exception as e:
        _report_failed_create_start(
            error=e,
            created_rollout_id=created_rollout_id,
            actions=actions,
            config=config,
        )
        raise
    return rollout, actions


def _report_failed_create_start(
    *,
    error: BaseException,
    created_rollout_id: str | None,
    actions: list[str],
    config: CLIConfigParameter,
) -> None:
    if created_rollout_id is None and not actions:
        return

    error_message = getattr(error, "message", None) or str(error)
    cleanup = f"tg beta endpoints rm {created_rollout_id}" if created_rollout_id else None

    if created_rollout_id is not None:
        hint = f"Created rollout {created_rollout_id} but failed to start it. Clean up with: {cleanup}"
        if actions:
            hint = f"{hint} Irreversible changes: {'; '.join(actions)}"
    else:
        hint = f"Rollout failed after irreversible changes: {'; '.join(actions)}"

    if config.json:
        payload: dict[str, Any] = {"error": error_message, "hint": hint}
        if created_rollout_id is not None:
            payload["id"] = created_rollout_id
            payload["type"] = "rollout"
            payload["command"] = cleanup
        if actions:
            payload["actions"] = actions
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        # Avoid the outer APIError handler printing a second, ID-less JSON error.
        raise SystemExit(1)

    if created_rollout_id is not None:
        error_console.print(
            f"[yellow]![/yellow] Created rollout [primary]{escape_rich_markup(created_rollout_id)}[/primary] "
            "but failed to start it."
        )
        error_console.print(f"  Clean up with: [primary]{escape_rich_markup(cleanup or '')}[/primary]")
        if actions:
            error_console.print(f"  Irreversible changes: {'; '.join(actions)}")
        return

    error_console.print(f"[yellow]![/yellow] {hint}")


def resolve_rollout_strategy(
    *,
    canary: bool,
    blue_green: bool,
    rolling: bool,
    steps: str | None,
    interval: str | None,
) -> tuple[Canary | None, BlueGreen | None, Rolling | None]:
    # Mutual exclusivity / canary-only options are enforced by Group validators above.
    if canary:
        return build_canary(steps=steps, interval=interval), None, None
    if blue_green:
        return None, BlueGreen(), None
    if rolling:
        return None, None, Rolling()
    raise ValueError("Must specify a rollout strategy: --blue-green, --canary, or --rolling.")


def build_canary(*, steps: str | None, interval: str | None) -> Canary:
    payload: Canary = {}
    if steps is not None:
        percents = parse_canary_steps(steps)
        payload["steps"] = [{"traffic": percent} for percent in percents]
    if interval is not None:
        payload["step_interval"] = normalize_duration(interval, option_name="--interval")
    return payload


def parse_canary_steps(value: str) -> list[int]:
    parts = [part.strip() for part in value.split(",")]
    if not parts or any(not part for part in parts):
        raise ValueError("--steps must be a comma-separated list of traffic percents, e.g. 10,50,100.")

    percents: list[int] = []
    for part in parts:
        try:
            percent = int(part)
        except ValueError as exc:
            raise ValueError(f"Invalid canary step {part!r}. Expected an integer percent.") from exc
        percents.append(percent)
    return percents


def _infer_active_source(endpoint: Endpoint, *, target_id: str) -> str:
    """Infer source as the sole non-target deployment with weight > 0.

    The target may already hold traffic (for example after a canceled rollout).
    Ambiguous (0 or 2+ remaining) requires an explicit ``--source``.
    """
    traffic_split = endpoint.traffic_split or []
    active = [
        traffic.deployment_id for traffic in traffic_split if traffic.weight > 0 and traffic.deployment_id != target_id
    ]
    if len(active) == 1:
        return active[0]
    if not active:
        raise ValueError(
            f"No active deployment found on endpoint {endpoint.id}. "
            "Pass --source <deployment-id-or-name> to specify the source."
        )
    raise ValueError(
        f"Multiple active deployments on endpoint {endpoint.id}: {', '.join(active)}. "
        "Pass --source <deployment-id-or-name> to choose the source."
    )


def _verify_rollout_pair(endpoint: Endpoint, *, source_id: str, target_id: str) -> None:
    if source_id == target_id:
        raise ValueError("Source and target deployments must be different.")

    deployment_ids = {d.id for d in (endpoint.deployments or []) if d.id}
    if source_id not in deployment_ids:
        raise ValueError(f"Source deployment {source_id} is not on endpoint {endpoint.id}.")
    if target_id not in deployment_ids:
        raise ValueError(f"Target deployment {target_id} is not on endpoint {endpoint.id}.")

    traffic_split = endpoint.traffic_split or []
    source_traffic = next((t for t in traffic_split if t.deployment_id == source_id), None)
    if source_traffic is None or source_traffic.weight <= 0:
        raise ValueError(
            f"Source deployment {source_id} is not receiving traffic. "
            "Rollout shifts traffic away from an active source deployment."
        )


async def _resolve_active_rollout(config: CLIConfigParameter, ref: str) -> Rollout:
    """Resolve the active rollout for an endpoint.

    Accepts endpoint ID/name, deployment ID/name, or rollout ID. The API allows
    only one active rollout per endpoint, so endpoint-scoped refs map directly
    to ``active_rollout_id``.
    """
    if ref.startswith("rol_"):
        return await resolve_rollout_by_id(config.client, ref)

    if ref.startswith("dep_"):
        return await _active_rollout_for_deployment(config.client, ref)

    if ref.startswith("ep_"):
        return await _active_rollout_for_endpoint(config, ref)

    # Bare name: endpoint first (same as retrieve), then deployment.
    try:
        return await _active_rollout_for_endpoint(config, ref)
    except NoActiveRolloutError:
        raise
    except ValueError:
        try:
            return await _active_rollout_for_deployment(config.client, ref)
        except (NoActiveRolloutError, AmbiguousDeploymentError):
            raise
        except ValueError:
            raise ValueError(
                f"No endpoint, deployment, or active rollout found for {ref!r}. "
                "Pass an endpoint ID (preferred), endpoint name, deployment ID/name, or rollout ID."
            ) from None


async def _active_rollout_for_endpoint(config: CLIConfigParameter, endpoint_ref: str) -> Rollout:
    endpoint = await resolve_endpoint(config, endpoint_ref)
    # List stubs (name lookup) can omit active_rollout_id — re-fetch for the
    # canonical value. ep_ refs already went through retrieve; trust None.
    if not endpoint_ref.startswith("ep_"):
        endpoint = await config.client.beta.endpoints.retrieve(endpoint.id)
    if endpoint.active_rollout_id:
        rollout = await config.client.beta.endpoints.rollouts.retrieve(
            endpoint.active_rollout_id,
            endpoint_id=endpoint.id,
        )
        return rollout

    # See fallback_active_rollout_from_list — server should have set activeRolloutId.
    rollout_lazy_loaded = await fallback_active_rollout_from_list(config.client, endpoint.id)
    if rollout_lazy_loaded is None:
        raise NoActiveRolloutError(f"No active rollout on endpoint {endpoint.id}.")
    return rollout_lazy_loaded


async def _active_rollout_for_deployment(client: AsyncClient, deployment_ref: str) -> Rollout:
    endpoint, _deployment_id = await resolve_deployment_id(client, deployment_ref)
    if endpoint.active_rollout_id is None:
        endpoint = await client.beta.endpoints.retrieve(endpoint.id)
    if endpoint.active_rollout_id:
        rollout = await client.beta.endpoints.rollouts.retrieve(
            endpoint.active_rollout_id,
            endpoint_id=endpoint.id,
        )
        return rollout

    # See fallback_active_rollout_from_list — server should have set activeRolloutId.
    rollout_lazy_loaded = await fallback_active_rollout_from_list(client, endpoint.id)
    if rollout_lazy_loaded is None:
        raise NoActiveRolloutError(f"No active rollout on endpoint {endpoint.id} (via deployment {deployment_ref!r}).")
    return rollout_lazy_loaded
