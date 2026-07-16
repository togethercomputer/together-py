from __future__ import annotations

import asyncio
from typing import List, Literal
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.padding import Padding

from together.types.beta import Endpoint, EndpointDeployment
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.types.beta.endpoints import AbExperiment, ShadowExperiment
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_model
from together.lib.cli.api.beta.endpoints._utils._find_endpoint_by_deployment import find_endpoint_by_deployment


async def retrieve(
    id: Annotated[str, Parameter(help="Endpoint ID (ep_...) or deployment ID (dep_...) to retrieve")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a beta endpoint or deployment."""
    if id.startswith("dep_"):
        await _retrieve_deployment(id, config=config)
        return

    await _retrieve_endpoint(id, config=config)


async def _retrieve_deployment(deployment_id: str, *, config: CLIConfigParameter) -> None:
    endpoint = await show_loading_status(
        "Resolving deployment...",
        find_endpoint_by_deployment(config.client, deployment_id),
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


async def _retrieve_endpoint(id: str, *, config: CLIConfigParameter) -> None:
    endpoint, ab_experiments, shadows = await show_loading_status(
        "Loading endpoint and related resources...",
        asyncio.gather(
            config.client.beta.endpoints.retrieve(id),
            config.client.beta.endpoints.ab_experiments.list(id),
            config.client.beta.endpoints.shadow_experiments.list(id, include_targets=True),
        ),
    )

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    **endpoint.to_dict(use_api_names=True),
                    "shadows": shadows.data,
                    "ab": ab_experiments.data,
                }
            ).decode("utf-8")
        )
        return

    render_header(endpoint, ab_experiments.data, shadows.data)

    traffic_split = endpoint.traffic_split or []
    deployments = endpoint.deployments or []
    # console.print(shadows)

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


def render_header(endpoint: Endpoint, ab_experiments: list[AbExperiment], shadows: list[ShadowExperiment]) -> None:
    url = f"https://api.together.ai/endpoints/{endpoint.id}"
    header_table = Table(expand=True, show_header=False, show_edge=False, show_lines=False, box=None, pad_edge=False)
    header_table.add_column("Key", justify="right", style="dim")
    header_table.add_column("Value", justify="left", ratio=4)
    header_table.add_row("  Inference Name", endpoint.name)
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

    panel = Panel(
        header_table,
        title=f"Endpoint Details for [bold][primary]{endpoint.name.split('/')[-1]}[/primary][/bold]",
        title_align="left",
    )
    console.print(panel)


def format_deployment_state(state: str) -> str:
    return {
        "DEPLOYMENT_STATE_PROVISIONING": "Provisioning",
        "DEPLOYMENT_STATE_READY": "[green]Ready[/green]",
        "DEPLOYMENT_STATE_SCALING": "[blue]Scaling[/blue]",
        "DEPLOYMENT_STATE_DEGRADED": "[red]Degraded[/red]",
        "DEPLOYMENT_STATE_FAILED": "[red]Failed[/red]",
        "DEPLOYMENT_STATE_STOPPED": "[dim]Stopped[/dim]",
        "DEPLOYMENT_STATE_STOPPING": "[yellow]Stopping[/yellow]",
    }.get(state, state)


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
