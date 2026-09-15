from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional, cast
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.endpoints.rollout import Rollout
from together.lib.cli.components.model_dump import print_model_dump
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.types.beta.endpoints.rollout_create_params import Canary, Metric, CanaryStep
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_endpoint

StrategyInput = Literal["canary", "rolling", "blue-green"]
FilterInput = Literal["active", "terminal"]
SDKFilter = Literal["ROLLOUT_FILTER_ACTIVE", "ROLLOUT_FILTER_TERMINAL"]

FILTER_MAP: Dict[FilterInput, SDKFilter] = {
    "active": "ROLLOUT_FILTER_ACTIVE",
    "terminal": "ROLLOUT_FILTER_TERMINAL",
}
ACTION_PROGRESS: Dict[str, str] = {
    "start": "Starting rollout...",
    "pause": "Pausing rollout...",
    "resume": "Resuming rollout...",
    "promote": "Promoting rollout...",
    "cancel": "Canceling rollout...",
}


async def create(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    *,
    source_deployment_id: Annotated[
        str,
        Parameter(
            name="source-deployment",
            help="Deployment that traffic shifts away from",
        ),
    ],
    target_deployment_id: Annotated[
        str,
        Parameter(
            name="target-deployment",
            help="Deployment that traffic shifts toward",
        ),
    ],
    strategy: Annotated[
        Optional[StrategyInput],
        Parameter(help="Rollout strategy to create: canary, rolling, or blue-green"),
    ] = None,
    canary_step: Annotated[
        Optional[List[str]],
        Parameter(
            name="canary-step",
            help="Canary step as TRAFFIC or TRAFFIC:REPLICAS. Can be used multiple times.",
        ),
    ] = None,
    step_interval: Annotated[
        Optional[str],
        Parameter(help="Canary soak interval between steps, such as 300s or 3m"),
    ] = None,
    final_source_replicas: Annotated[
        Optional[int],
        Parameter(help="Final replica count for the source deployment"),
    ] = None,
    final_target_replicas: Annotated[
        Optional[int],
        Parameter(help="Target replica floor at completion"),
    ] = None,
    metric: Annotated[
        Optional[List[str]],
        Parameter(
            help=(
                "Metric gate JSON object. Can be used multiple times. "
                "Accepts SDK snake_case or API camelCase keys."
            ),
        ),
    ] = None,
    start: Annotated[
        bool,
        Parameter(help="Start the rollout immediately after creating it", negative=()),
    ] = False,
    config: CLIConfigParameter,
) -> None:
    """Create a rollout for an endpoint."""
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    rollout = await show_loading_status(
        "Creating rollout...",
        config.client.beta.endpoints.rollouts.create(
            endpoint.id,
            source_deployment_id=source_deployment_id,
            target_deployment_id=target_deployment_id,
            **_build_create_kwargs(
                strategy=strategy,
                canary_step=canary_step,
                step_interval=step_interval,
                final_source_replicas=final_source_replicas,
                final_target_replicas=final_target_replicas,
                metric=metric,
            ),
        ),
    )

    if start:
        rollout = await show_loading_status(
            "Starting rollout...",
            config.client.beta.endpoints.rollouts.start(rollout.id, endpoint_id=endpoint.id),
        )

    if config.json:
        console.print_json(openapi_dumps(rollout).decode("utf-8"))
        return

    console.print(f"[green]OK[/green] Rollout created [dim]({rollout.id})[/dim]")
    if not start:
        console.print(f"  To start it: [primary]tg beta endpoints rollouts start {endpoint.id} {rollout.id}[/primary]")
    print_rollout_detail(rollout)


async def preview_defaults(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    *,
    source_deployment_id: Annotated[
        str,
        Parameter(name="source-deployment", help="Deployment that traffic shifts away from"),
    ],
    target_deployment_id: Annotated[
        str,
        Parameter(name="target-deployment", help="Deployment that traffic shifts toward"),
    ],
    strategy: Annotated[
        Optional[StrategyInput],
        Parameter(help="Rollout strategy to preview: canary, rolling, or blue-green"),
    ] = None,
    canary_step: Annotated[
        Optional[List[str]],
        Parameter(
            name="canary-step",
            help="Canary step as TRAFFIC or TRAFFIC:REPLICAS. Can be used multiple times.",
        ),
    ] = None,
    step_interval: Annotated[
        Optional[str],
        Parameter(help="Canary soak interval between steps, such as 300s or 3m"),
    ] = None,
    final_source_replicas: Annotated[
        Optional[int],
        Parameter(help="Final replica count for the source deployment"),
    ] = None,
    final_target_replicas: Annotated[
        Optional[int],
        Parameter(help="Target replica floor at completion"),
    ] = None,
    metric: Annotated[
        Optional[List[str]],
        Parameter(
            help=(
                "Metric gate JSON object. Can be used multiple times. "
                "Accepts SDK snake_case or API camelCase keys."
            ),
        ),
    ] = None,
    config: CLIConfigParameter,
) -> None:
    """Preview the rollout defaults the API would choose."""
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    preview = await show_loading_status(
        "Previewing rollout defaults...",
        config.client.beta.endpoints.rollouts.preview_defaults(
            endpoint.id,
            source_deployment_id=source_deployment_id,
            target_deployment_id=target_deployment_id,
            **_build_create_kwargs(
                strategy=strategy,
                canary_step=canary_step,
                step_interval=step_interval,
                final_source_replicas=final_source_replicas,
                final_target_replicas=final_target_replicas,
                metric=metric,
            ),
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(preview).decode("utf-8"))
        return

    print_model_dump(preview, show_nulls=False, only_set_fields=True)


async def list(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    filter: Annotated[Optional[FilterInput], Parameter(help="Narrow results to active or terminal rollouts")] = None,
    limit: Annotated[Optional[int], Parameter(help="Maximum number of rollouts to return. Max 500.")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List rollouts for an endpoint."""
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    response = await show_loading_status(
        "Loading rollouts...",
        config.client.beta.endpoints.rollouts.list(
            endpoint.id,
            after=after or omit,
            filter=FILTER_MAP[filter] if filter else omit,
            limit=limit if limit is not None else omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_rollouts_table(response.data or [], endpoint_id=endpoint.id)
    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(
            f"  [dim]-[/dim] [white]tg beta endpoints rollouts ls {endpoint.id} --after {response.next_cursor}[/white]"
        )


async def retrieve(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve rollout details."""
    rollout = await _retrieve_rollout(endpoint_id_or_name, rollout_id, config=config)
    if config.json:
        console.print_json(openapi_dumps(rollout).decode("utf-8"))
        return

    print_rollout_detail(rollout)


async def start(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Start a pending rollout."""
    await _run_rollout_action("start", endpoint_id_or_name, rollout_id, config=config)


async def pause(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    reason: Annotated[Optional[str], Parameter(help="Human-readable pause reason")] = None,
    etag: Annotated[Optional[str], Parameter(help="Rollout etag for optimistic concurrency")] = None,
    config: CLIConfigParameter,
) -> None:
    """Request a running rollout to pause."""
    await _run_rollout_action("pause", endpoint_id_or_name, rollout_id, reason=reason, etag=etag, config=config)


async def resume(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    etag: Annotated[Optional[str], Parameter(help="Rollout etag for optimistic concurrency")] = None,
    config: CLIConfigParameter,
) -> None:
    """Resume a paused rollout."""
    await _run_rollout_action("resume", endpoint_id_or_name, rollout_id, etag=etag, config=config)


async def promote(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    etag: Annotated[Optional[str], Parameter(help="Rollout etag for optimistic concurrency")] = None,
    config: CLIConfigParameter,
) -> None:
    """Promote a rollout immediately."""
    await _run_rollout_action("promote", endpoint_id_or_name, rollout_id, etag=etag, config=config)


async def cancel(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    reason: Annotated[str, Parameter(help="Human-readable cancel reason")],
    disposition: Annotated[
        Optional[Literal["freeze", "revert"]],
        Parameter(help="Cancel disposition. freeze preserves current traffic split; revert is API-rejected."),
    ] = None,
    etag: Annotated[Optional[str], Parameter(help="Rollout etag for optimistic concurrency")] = None,
    config: CLIConfigParameter,
) -> None:
    """Cancel a running, paused, or stabilizing rollout."""
    sdk_disposition = None
    if disposition == "freeze":
        sdk_disposition = "CANCEL_DISPOSITION_FREEZE"
    elif disposition == "revert":
        sdk_disposition = "CANCEL_DISPOSITION_REVERT"

    await _run_rollout_action(
        "cancel",
        endpoint_id_or_name,
        rollout_id,
        reason=reason,
        etag=etag,
        disposition=sdk_disposition,
        config=config,
    )


async def delete(
    endpoint_id_or_name: Annotated[str, Parameter(name="endpoint", help="Endpoint ID (ep_...) or name")],
    rollout_id: Annotated[str, Parameter(name="rollout", help="Rollout ID")],
    *,
    etag: Annotated[Optional[str], Parameter(help="Rollout etag for optimistic concurrency")] = None,
    config: CLIConfigParameter,
) -> None:
    """Delete a rollout record."""
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    response = await show_loading_status(
        "Deleting rollout...",
        config.client.beta.endpoints.rollouts.delete(
            rollout_id,
            endpoint_id=endpoint.id,
            etag=etag or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[green]OK[/green] Deleted rollout {rollout_id}")


async def _run_rollout_action(
    action: Literal["start", "pause", "resume", "promote", "cancel"],
    endpoint_id_or_name: str,
    rollout_id: str,
    *,
    config: CLIConfigParameter,
    reason: str | None = None,
    etag: str | None = None,
    disposition: str | None = None,
) -> None:
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    rollouts = config.client.beta.endpoints.rollouts
    if action == "start":
        request = rollouts.start(rollout_id, endpoint_id=endpoint.id)
    elif action == "pause":
        request = rollouts.pause(rollout_id, endpoint_id=endpoint.id, reason=reason or omit, etag=etag or omit)
    elif action == "resume":
        request = rollouts.resume(rollout_id, endpoint_id=endpoint.id, etag=etag or omit)
    elif action == "promote":
        request = rollouts.promote(rollout_id, endpoint_id=endpoint.id, etag=etag or omit)
    else:
        request = rollouts.cancel(
            rollout_id,
            endpoint_id=endpoint.id,
            reason=cast(str, reason),
            disposition=cast(Any, disposition) or omit,
            etag=etag or omit,
        )

    rollout = await show_loading_status(ACTION_PROGRESS[action], request)
    if config.json:
        console.print_json(openapi_dumps(rollout).decode("utf-8"))
        return

    console.print(f"[green]OK[/green] Rollout {action} accepted [dim]({rollout.id})[/dim]")
    print_rollout_detail(rollout)


async def _retrieve_rollout(endpoint_id_or_name: str, rollout_id: str, *, config: CLIConfigParameter) -> Rollout:
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, endpoint_id_or_name))
    return await show_loading_status(
        "Loading rollout...",
        config.client.beta.endpoints.rollouts.retrieve(rollout_id, endpoint_id=endpoint.id),
    )


def _build_create_kwargs(
    *,
    strategy: StrategyInput | None,
    canary_step: List[str] | None,
    step_interval: str | None,
    final_source_replicas: int | None,
    final_target_replicas: int | None,
    metric: List[str] | None,
) -> Dict[str, Any]:
    if strategy is None and (canary_step or step_interval):
        strategy = "canary"

    kwargs: Dict[str, Any] = {
        "blue_green": omit,
        "canary": omit,
        "rolling": omit,
        "final_source_replicas": final_source_replicas if final_source_replicas is not None else omit,
        "final_target_replicas": final_target_replicas if final_target_replicas is not None else omit,
        "metrics": _parse_metrics(metric) if metric else omit,
    }

    if strategy == "blue-green":
        kwargs["blue_green"] = {}
    elif strategy == "rolling":
        kwargs["rolling"] = {}
    elif strategy == "canary":
        kwargs["canary"] = _build_canary(canary_step=canary_step, step_interval=step_interval)

    return kwargs


def _build_canary(*, canary_step: List[str] | None, step_interval: str | None) -> Canary:
    canary: Canary = {}
    if step_interval:
        canary["step_interval"] = step_interval
    if canary_step:
        canary["steps"] = _parse_canary_steps(canary_step)
    return canary


def _parse_canary_steps(values: List[str]) -> List[CanaryStep]:
    steps: List[CanaryStep] = []
    for value in values:
        traffic_raw, separator, replicas_raw = value.partition(":")
        try:
            traffic = int(traffic_raw)
            replicas = int(replicas_raw) if separator else None
        except ValueError:
            raise ValueError(f"Invalid canary step {value!r}. Expected TRAFFIC or TRAFFIC:REPLICAS.") from None
        if traffic <= 0 or traffic > 100:
            raise ValueError("Canary step traffic must be between 1 and 100.")
        if replicas is not None and replicas < 0:
            raise ValueError("Canary step replicas must be greater than or equal to 0.")
        step: CanaryStep = {"traffic": traffic}
        if replicas is not None:
            step["replicas"] = replicas
        steps.append(step)
    return steps


def _parse_metrics(values: List[str]) -> List[Metric]:
    metrics: List[Metric] = []
    for value in values:
        try:
            raw = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid metric JSON: {e.msg}") from None
        if not isinstance(raw, dict):
            raise ValueError("Each --metric value must be a JSON object.")
        metrics.append(cast(Metric, _normalize_metric_keys(raw)))
    return metrics


def _normalize_metric_keys(metric: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(metric)
    _move_key(result, "regressionCheck", "regression_check")
    _move_key(result, "thresholdCheck", "threshold_check")

    regression = result.get("regression_check")
    if isinstance(regression, dict):
        _move_key(regression, "maxRegressionPercent", "max_regression_percent")

    return result


def _move_key(values: Dict[str, Any], old: str, new: str) -> None:
    if old in values and new not in values:
        values[new] = values.pop(old)


def print_rollout_detail(rollout: Rollout) -> None:
    print_model_dump(rollout, show_nulls=False, only_set_fields=True)


def print_rollouts_table(rollouts: List[Rollout], *, endpoint_id: str) -> None:
    table = ListTable(title="Endpoint Rollouts", empty_message=f"No rollouts found for endpoint {endpoint_id}.")
    table.add_column("Created", width=16, no_wrap=True)
    table.add_primary_column("Rollout", ratio=2)
    table.add_column("State")
    table.add_column("Strategy")
    table.add_column("Traffic")
    table.add_column("Step")

    for rollout in rollouts:
        table.add_row(
            format_datetime(rollout.created_at),
            rollout.id,
            _format_state(rollout.state),
            rollout.strategy.replace("ROLLOUT_STRATEGY_TYPE_", "").replace("_", "-").lower(),
            _format_traffic(rollout.current_traffic_percent),
            _format_step(rollout),
        )

    console.print(table)


def _format_state(state: str) -> str:
    label = state.replace("ROLLOUT_STATE_", "")
    color = {
        "RUNNING": "green",
        "PAUSED": "yellow",
        "STABILIZING": "yellow",
        "PENDING": "yellow",
        "SYSTEM_PAUSED": "yellow",
        "PAUSING": "yellow",
        "CANCELLING": "yellow",
        "COMPLETED": "green",
        "CANCELED": "dim",
    }.get(label, "white")
    return f"[{color}]{label}[/{color}]"


def _format_traffic(value: int | None) -> str:
    if value is None:
        return "-"
    return f"{value}%"


def _format_step(rollout: Rollout) -> str:
    current = rollout.current_step
    total = rollout.status.total_steps if rollout.status else None
    if current is None or total is None:
        return "-"
    return f"{current + 1}/{total}"
