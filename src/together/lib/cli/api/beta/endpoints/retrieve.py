from __future__ import annotations

import asyncio
from typing import List, Literal
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape as escape_rich_markup
from rich.columns import Columns
from rich.padding import Padding

from together.pagination import AsyncCursorPagination
from together.types.beta import Endpoint, EndpointDeployment
from together._exceptions import APIError
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.endpoints import Rollout, AbExperiment, ShadowExperiment
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.types.beta.endpoints.rollout import StatusStep, StatusCondition, StatusStepMetric, StatusConditionMetric
from together.lib.cli.api.beta.endpoints._utils._rollouts import resolve_rollout_by_id
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_model, resolve_endpoint
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import resolve_deployment_id


async def retrieve(
    id: Annotated[
        str,
        Parameter(
            help=(
                "Endpoint name, endpoint ID (ep_...), deployment name, deployment ID (dep_...), "
                "or rollout ID (rol_...) to retrieve"
            )
        ),
    ],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a beta endpoint, deployment, or rollout."""
    if id.startswith("dep_"):
        await _retrieve_deployment(id, config=config)
        return

    if id.startswith("rol_"):
        await _retrieve_rollout(id, config=config)
        return

    if id.startswith("ep_"):
        await _retrieve_endpoint(id, config=config)
        return

    try:
        endpoint = await resolve_endpoint(config, id)
    except ValueError:
        # Not an endpoint name — try as a deployment name before failing.
        await _retrieve_deployment(id, config=config)
        return

    await _retrieve_endpoint(endpoint.id, config=config)


async def _retrieve_deployment(deployment_id_or_name: str, *, config: CLIConfigParameter) -> None:
    endpoint, deployment_id = await show_loading_status(
        "Resolving deployment...",
        resolve_deployment_id(config.client, deployment_id_or_name),
    )
    deployment = await show_loading_status(
        "Loading deployment...",
        config.client.beta.endpoints.deployments.retrieve(
            deployment_id,
            endpoint_id=endpoint.id,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(deployment).decode("utf-8"))
        return

    print_deployment_detail(deployment)


async def _retrieve_rollout(rollout_id: str, *, config: CLIConfigParameter) -> None:
    rollout = await show_loading_status(
        "Resolving rollout...",
        resolve_rollout_by_id(config.client, rollout_id),
    )

    if config.json:
        console.print_json(openapi_dumps(rollout).decode("utf-8"))
        return

    traffic, step_text = format_rollout_progress(rollout)

    console.print(f"[dim][primary]Rollout ID:[/primary][/dim]\t{rollout.id}")
    console.print(f"[dim][primary]Endpoint ID:[/primary][/dim]\t{rollout.endpoint_id}")
    console.print(f"[dim][primary]Source Deployment:[/primary][/dim]\t{rollout.source_deployment_id}")
    console.print(f"[dim][primary]Target Deployment:[/primary][/dim]\t{rollout.target_deployment_id}")
    console.print(f"[dim][primary]Strategy:[/primary][/dim]\t{format_rollout_strategy(rollout.strategy)}")
    console.print(f"[dim][primary]State:[/primary][/dim]\t\t{format_rollout_state(rollout.state)}")
    console.print(f"[dim][primary]Traffic:[/primary][/dim]\t{traffic}")
    console.print(f"[dim][primary]Step:[/primary][/dim]\t\t{step_text}")
    for label, value in rollout_reason_rows(rollout):
        console.print(f"[dim][primary]{label}:[/primary][/dim]\t{value}")
    console.print(f"[dim][primary]Created at:[/primary][/dim]\t{format_datetime(rollout.created_at)}")


async def _retrieve_endpoint(id: str, *, config: CLIConfigParameter) -> None:
    endpoint, ab_experiments, shadows, rollout = await show_loading_status(
        "Loading endpoint and related resources...",
        _load_endpoint_resources(config, id),
    )

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    **endpoint.to_dict(use_api_names=True),
                    "shadows": shadows.data,
                    "ab": ab_experiments.data,
                    "rollout": rollout,
                }
            ).decode("utf-8")
        )
        return

    render_header(endpoint, ab_experiments.data, shadows.data, rollout)
    await render_deployments(endpoint, config=config)


async def _load_endpoint_resources(
    config: CLIConfigParameter, id: str
) -> tuple[Endpoint, AsyncCursorPagination[AbExperiment], AsyncCursorPagination[ShadowExperiment], Rollout | None]:
    """Load endpoint + related resources.

    Resolve the current rollout via ``active_rollout_id`` rather than
    ``ROLLOUT_FILTER_ACTIVE`` — that filter can omit paused / system-paused
    rollouts, which should still show in the retrieve printout.
    """
    endpoint, ab_experiments, shadows = await asyncio.gather(
        config.client.beta.endpoints.retrieve(id),
        config.client.beta.endpoints.ab_experiments.list(id),
        config.client.beta.endpoints.shadow_experiments.list(id, include_targets=True),
    )

    rollout: Rollout | None = None
    if endpoint.active_rollout_id:
        # active_rollout_id can be stale; don't fail the whole retrieve on a 404.
        try:
            rollout = await config.client.beta.endpoints.rollouts.retrieve(
                endpoint.active_rollout_id,
                endpoint_id=endpoint.id,
            )
        except APIError:
            pass

    return endpoint, ab_experiments, shadows, rollout


async def render_deployments(endpoint: Endpoint, *, config: CLIConfigParameter) -> None:
    traffic_split = endpoint.traffic_split or []
    deployments = endpoint.deployments or []

    if len(traffic_split) > 1:
        console.print(f"\nTraffic Splits")
        console.print(f"[dim]Each deployment serves a fixed share of traffic.[/dim]")

        traffic_split_table = Table(expand=True, show_header=False, padding=(0, 0), box=None)
        if endpoint.deployments:
            row: List[Panel] = []
            for i, traffic in enumerate(traffic_split):
                deployment = next(d for d in endpoint.deployments if d.id == traffic.deployment_id)
                name = deployment.name.split("/")[-1]

                columns = Columns(expand=True)
                columns.add_renderable(name)
                traffic_split_table.add_column(ratio=int(traffic.weight * 100))
                panel = Panel(columns, border_style=traffic_split_colors[i])

                row.append(panel)
            traffic_split_table.add_row(*row)
        console.print(Padding(traffic_split_table, (0, 0)))

    if len(traffic_split) == 0:
        console.print("\n[yellow]No traffic split configured.[/yellow]")
        console.print("[dim]This endpoint will not serve any inference until a traffic_split is set.[/dim]")

    deployments_table = ListTable(title="Deployments", empty_message="No deployments found", show_lines=False)
    deployments_table.add_primary_column("Deployment", ratio=2)
    deployments_table.add_column("Model")
    deployments_table.add_column("Estimated Traffic")
    deployments_table.add_column("")
    for i, deployment in enumerate(deployments):
        name = deployment.name.split("/")[-1]

        model = (await resolve_model(config, deployment.model)).name

        replicas = f"{deployment.ready_replicas or 0} / {deployment.desired_replicas or 0}"
        estimated_traffic = format_estimated_traffic(deployment.estimated_effective_traffic_share)

        deployments_table.add_row(
            f"Name: {name}\n[dim]  ID: {deployment.id}[/dim]",
            model,
            estimated_traffic,
            f"  Status: {format_deployment_state(deployment.state)}\nReplicas: {replicas}",
        )
        if i < len(deployments) - 1:
            deployments_table.add_row()
    console.print(Padding(deployments_table, (0, 0)))


traffic_split_colors = [
    "#578db2",
    "#ad46ff",
    "#f6339a",
    "#00bba7",
    "#2e6386",
    "#578db2",
    "#ad46ff",
    "#f6339a",
    "#00bba7",
    "#2e6386",
]


def _readable_visibility(
    visibility: Literal["VISIBILITY_PUBLIC", "VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"] | None,
) -> str:
    if visibility is None:
        return "Unknown"
    return {
        "VISIBILITY_PUBLIC": "Public",
        "VISIBILITY_PRIVATE": "Private",
        "VISIBILITY_INTERNAL": "Internal",
    }[visibility]


def render_header(
    endpoint: Endpoint,
    ab_experiments: list[AbExperiment],
    shadows: list[ShadowExperiment],
    rollout: Rollout | None,
) -> None:
    url = f"https://api.together.ai/endpoints/{endpoint.id}"
    header_table = Table(expand=True, show_header=False, show_edge=False, show_lines=False, box=None, pad_edge=False)
    header_table.add_column("Key", justify="right", style="dim")
    header_table.add_column("Value", justify="left", ratio=4)
    header_table.add_row("  Endpoint string", endpoint.name)
    header_table.add_row("  Endpoint ID", endpoint.id)
    header_table.add_row("  Created at", format_datetime(endpoint.created_at))
    if endpoint.updated_at:
        header_table.add_row("  Updated at", format_datetime(endpoint.updated_at))
    header_table.add_row("  Visibility", _readable_visibility(endpoint.visibility))
    header_table.add_row("  Web URL", f"[link={url}]{url}[/link]")

    # A/B Experiments
    if len(ab_experiments) > 0:
        header_table.add_row("", "")
        header_table.add_row("  A/B Experiments", "")
        for experiment in ab_experiments:
            for member in experiment.members:
                header_table.add_row(
                    "",
                    f"[dim]{member.role.replace('AB_EXPERIMENT_MEMBER_ROLE_', '').title()}:[/dim] {member.deployment_id} ({member.percent}%)",
                )

    # Traffic Shadowing
    if len(shadows) > 0:
        header_table.add_row("", "")
        header_table.add_row("  Traffic Shadow", "")
        for shadow in shadows:
            shadow_text = ""

            # TODO: Cover all cases
            uniform_sampling = getattr(shadow.source.endpoint.sampling, "uniform", None)
            if uniform_sampling:
                shadow_text = f"[dim]shadowing {int(uniform_sampling.rate * 100)}% of endpoint traffic[/dim]"
            for target in shadow.targets or []:
                if target.target_deployment_id is not None:  # type: ignore
                    target_deployment = next(d for d in endpoint.deployments if d.id == target.target_deployment_id)
                    header_table.add_row("", f"{target_deployment.name.split('/')[-1]} {shadow_text}")

    # Active Rollout
    if rollout is not None:
        header_table.add_row("", "")
        header_table.add_row("  Active Rollout", "")
        source_name = _deployment_short_name(endpoint, rollout.source_deployment_id)
        target_name = _deployment_short_name(endpoint, rollout.target_deployment_id)
        header_table.add_row("", f"[dim]ID:[/dim] {rollout.id}")
        header_table.add_row(
            "",
            f"[dim]State:[/dim] {format_rollout_state(rollout.state)}  "
            f"[dim]Strategy:[/dim] {format_rollout_strategy(rollout.strategy)}",
        )
        header_table.add_row("", f"[dim]Source → Target:[/dim] {source_name} → {target_name}")
        traffic, step_text = format_rollout_progress(rollout)
        header_table.add_row("", f"[dim]Traffic:[/dim] {traffic}  [dim]Step:[/dim] {step_text}")
        for label, value in rollout_reason_rows(rollout):
            header_table.add_row("", f"[dim]{label}:[/dim] {value}")

    panel = Panel(
        header_table,
        title=f"Endpoint Details for [bold][primary]{endpoint.name.split('/')[-1]}[/primary][/bold]",
        title_align="left",
    )
    console.print(panel)


def _deployment_short_name(endpoint: Endpoint, deployment_id: str) -> str:
    for deployment in endpoint.deployments or []:
        if deployment.id == deployment_id:
            return deployment.name.split("/")[-1]
    return deployment_id


def format_rollout_progress(rollout: Rollout) -> tuple[str, str]:
    traffic = "—" if rollout.current_traffic_percent is None else f"{rollout.current_traffic_percent}%"
    # current_step is zero-based; display as 1-based for humans.
    if rollout.current_step is None:
        step_text = "—"
    else:
        total = rollout.status.total_steps if rollout.status else "?"
        step_text = f"{rollout.current_step + 1}/{total}"
        current = _step_at(rollout, rollout.current_step)
        if current is not None and current.state:
            step_text = f"{step_text} {format_step_state(current.state)}"
    return traffic, step_text


_ROLLOUT_STATE_STYLES = {
    "ROLLOUT_STATE_RUNNING": "green",
    "ROLLOUT_STATE_PAUSED": "yellow",
    "ROLLOUT_STATE_PAUSING": "yellow",
    "ROLLOUT_STATE_SYSTEM_PAUSED": "yellow",
    "ROLLOUT_STATE_STABILIZING": "blue",
    "ROLLOUT_STATE_CANCELLING": "yellow",
    "ROLLOUT_STATE_PENDING": "dim",
    "ROLLOUT_STATE_COMPLETED": "green",
    "ROLLOUT_STATE_CANCELED": "red",
}

_STEP_STATE_STYLES = {
    "ROLLOUT_STEP_STATE_PENDING": ("dim", "Pending"),
    "ROLLOUT_STEP_STATE_RUNNING": ("blue", "Running"),
    "ROLLOUT_STEP_STATE_PASSED": ("green", "Passed"),
    "ROLLOUT_STEP_STATE_FAILED": ("red", "Failed"),
    "ROLLOUT_STEP_STATE_PAUSED": ("yellow", "Paused"),
    "ROLLOUT_STEP_STATE_CANCELED": ("red", "Canceled"),
    "ROLLOUT_STEP_STATE_SKIPPED": ("dim", "Skipped"),
}

_OPERATOR_SYMBOLS = {
    "THRESHOLD_OPERATOR_GT": ">",
    "THRESHOLD_OPERATOR_GTE": ">=",
    "THRESHOLD_OPERATOR_LT": "<",
    "THRESHOLD_OPERATOR_LTE": "<=",
}

_VERDICT_STYLES = {
    "METRIC_VERDICT_PASS": ("green", "Pass"),
    "METRIC_VERDICT_BREACHED": ("red", "Breached"),
    "METRIC_VERDICT_UNAVAILABLE": ("yellow", "Unavailable"),
}


def _enum_label(value: str, prefix: str) -> str:
    if value.startswith(prefix):
        value = value[len(prefix) :]
    return value.replace("_", " ").title()


def format_rollout_state(state: str) -> str:
    label = state.replace("ROLLOUT_STATE_", "").replace("_", " ").title()
    style = _ROLLOUT_STATE_STYLES.get(state)
    return f"[{style}]{label}[/{style}]" if style else label


def format_rollout_strategy(strategy: str) -> str:
    return strategy.replace("ROLLOUT_STRATEGY_TYPE_", "").replace("_", " ").title()


def format_step_state(state: str) -> str:
    style, text = _STEP_STATE_STYLES.get(
        state,
        (None, _enum_label(state, "ROLLOUT_STEP_STATE_")),
    )
    return f"[{style}]{text}[/{style}]" if style else text


def _status_steps(rollout: Rollout) -> list[StatusStep]:
    if not rollout.status:
        return []
    return list(rollout.status.steps or [])


def _step_at(rollout: Rollout, index: int) -> StatusStep | None:
    steps = _status_steps(rollout)
    for step in steps:
        if step.step_index == index:
            return step
    if 0 <= index < len(steps) and steps[index].step_index is None:
        return steps[index]
    return None


def _gate_status_step(rollout: Rollout) -> StatusStep | None:
    """Step that tripped a gate, else the current step."""
    failed = [step for step in _status_steps(rollout) if step.state == "ROLLOUT_STEP_STATE_FAILED"]
    if failed:
        return failed[-1]
    if rollout.current_step is not None:
        return _step_at(rollout, rollout.current_step)
    return None


def format_status_step_line(step: StatusStep, *, fallback_index: int | None = None) -> str:
    index = step.step_index if step.step_index is not None else fallback_index
    parts = [f"{index + 1}" if index is not None else "?"]
    if step.target_traffic_percent is not None:
        parts.append(f"{step.target_traffic_percent}%")
    if step.state:
        parts.append(format_step_state(step.state))
    return " ".join(parts)


def format_rollout_condition_summary(condition: StatusCondition) -> str | None:
    """Humanize ``status.condition`` category/message/step into one line."""
    parts: list[str] = []
    if condition.category:
        parts.append(_enum_label(condition.category, "ROLLOUT_FAILURE_CATEGORY_"))
    if condition.message:
        message = escape_rich_markup(condition.message)
        parts.append(message if not parts else f"— {message}")
    if condition.at_step is not None:
        # at_step is zero-based; display as 1-based to match Step progress.
        parts.append(f"(step {condition.at_step + 1})")
    return " ".join(parts) if parts else None


def format_condition_metric_line(metric: StatusConditionMetric | StatusStepMetric) -> str:
    """One-line gate result: name/stat, observed values, criteria, verdict."""
    name = escape_rich_markup(metric.name or "metric")
    if metric.stat == "METRIC_STAT_TYPE_PERCENTILE" and metric.percentile is not None:
        stat = f"p{metric.percentile}"
    elif metric.stat:
        stat = _enum_label(metric.stat, "METRIC_STAT_TYPE_").lower()
    else:
        stat = None
    label = f"{name} {stat}" if stat else name

    details: list[str] = []
    if metric.source_value is not None:
        details.append(f"source={metric.source_value:g}")
    if metric.check == "METRIC_CHECK_TYPE_REGRESSION":
        if metric.target_value is not None:
            details.append(f"target={metric.target_value:g}")
        if metric.max_regression_percent is not None:
            details.append(f"max regression {metric.max_regression_percent:g}%")
    else:
        if metric.target_value is not None:
            details.append(f"value={metric.target_value:g}")
        if metric.threshold is not None:
            op = _OPERATOR_SYMBOLS.get(metric.operator or "", "")
            threshold = f"{metric.threshold:g}"
            details.append(f"threshold {op} {threshold}".strip() if op else f"threshold {threshold}")

    body = f"{label}: {', '.join(details)}" if details else label
    if metric.verdict:
        style, text = _VERDICT_STYLES.get(
            metric.verdict,
            (None, _enum_label(metric.verdict, "METRIC_VERDICT_")),
        )
        verdict = f"[{style}]{text}[/{style}]" if style else text
        body = f"{body}  {verdict}"
    if metric.failure_reason:
        body = f"{body} — {escape_rich_markup(metric.failure_reason)}"
    return body


def rollout_reason_rows(rollout: Rollout) -> list[tuple[str, str]]:
    """Label/value rows for steps, condition, metric gates, and pause_info."""
    rows: list[tuple[str, str]] = []
    steps = _status_steps(rollout)
    if len(steps) > 1 and any(step.state for step in steps):
        rows.append(
            (
                "Steps",
                " · ".join(format_status_step_line(step, fallback_index=i) for i, step in enumerate(steps)),
            )
        )

    condition = rollout.status.condition if rollout.status else None
    condition_metrics = list(condition.metrics or []) if condition is not None else []
    if condition is not None:
        summary = format_rollout_condition_summary(condition)
        if summary:
            rows.append(("Reason", summary))
        for condition_metric in condition_metrics:
            rows.append(("Metric", format_condition_metric_line(condition_metric)))

    gate = _gate_status_step(rollout)
    if gate is not None and gate.failure_reason:
        # Avoid duplicating condition.message when the step echoes it into failureReason.
        if condition is None or gate.failure_reason != condition.message:
            label = "Reason" if not any(row[0] == "Reason" for row in rows) else "Failure"
            rows.append((label, escape_rich_markup(gate.failure_reason)))
    if not condition_metrics and gate is not None:
        for gate_metric in gate.metrics or []:
            rows.append(("Metric", format_condition_metric_line(gate_metric)))

    pause = rollout.pause_info
    if pause is not None and pause.reason:
        # Avoid duplicating condition.message when the system echoes it into pauseInfo.
        if condition is None or pause.reason != condition.message:
            rows.append(("Pause reason", escape_rich_markup(pause.reason)))
    return rows


_DEPLOYMENT_STATE_LABELS = {
    "DEPLOYMENT_STATE_PROVISIONING": "Provisioning",
    "DEPLOYMENT_STATE_READY": "[green]Ready[/green]",
    "DEPLOYMENT_STATE_SCALING": "[blue]Scaling[/blue]",
    "DEPLOYMENT_STATE_DEGRADED": "[red]Degraded[/red]",
    "DEPLOYMENT_STATE_FAILED": "[red]Failed[/red]",
    "DEPLOYMENT_STATE_STOPPED": "[dim]Stopped[/dim]",
    "DEPLOYMENT_STATE_STOPPING": "[yellow]Stopping[/yellow]",
}


def format_deployment_state(state: str) -> str:
    return _DEPLOYMENT_STATE_LABELS.get(state, state)


def format_estimated_traffic(share: float | None) -> str:
    if share is None:
        return "—"
    return f"{round(share * 100)}%"


def print_deployment_detail(deployment: EndpointDeployment | None) -> None:
    if deployment is None:
        console.print("Deployment not found.")
        return
    console.print(f"[dim][primary]Name:[/primary][/dim]\t\t[bold]{deployment.name}[/bold]")
    console.print(f"[dim][primary]ID:[/primary][/dim]\t\t{deployment.id}")
    console.print(f"[dim][primary]Endpoint:[/primary][/dim]\t{deployment.endpoint_id}")
    console.print(f"[dim][primary]Project:[/primary][/dim]\t{deployment.project_id or ''}")
    console.print(f"[dim][primary]Model:[/primary][/dim]\t\t{deployment.api_model_id}")
    console.print(f"[dim][primary]Config:[/primary][/dim]\t{deployment.config_id}")
    console.print(f"[dim][primary]Hardware:[/primary][/dim]\t{deployment.hardware}")
    console.print(f"[dim][primary]State:[/primary][/dim]\t\t{deployment.status.state}")
    console.print(f"[dim][primary]Message:[/primary][/dim]\t{deployment.status.message}")
    console.print(f"[dim][primary]Ready:[/primary][/dim]\t\t{deployment.status.ready_replicas}")
    console.print(
        "[dim][primary]Replicas:[/primary][/dim]\t"
        f"min: {deployment.autoscaling.min_replicas} "
        f"max: {deployment.autoscaling.max_replicas}"
    )
    console.print(
        f"[dim][primary]Traffic:[/primary][/dim]\t{format_estimated_traffic(deployment.estimated_effective_traffic_share)}"
    )
    console.print(f"[dim][primary]ETag:[/primary][/dim]\t\t{deployment.etag}")
    console.print(f"[dim][primary]Created:[/primary][/dim]\t{format_datetime(deployment.created_at)}")
