from __future__ import annotations

from typing import Any, Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter

EndpointIDParameter = Annotated[str, Parameter(help="Endpoint ID (ep_...)")]
DeploymentIDParameter = Annotated[str, Parameter(help="Deployment ID (dep_...)")]
AdapterIDParameter = Annotated[str, Parameter(help="Adapter attachment ID (dad_...)")]
AdapterModelIDParameter = Annotated[str, Parameter(help="Adapter model ID (ml_...) to attach")]
AdapterModelIDOption = Annotated[
    Optional[str],
    Parameter(help="Deprecated optional cross-check adapter model ID (ml_...)"),
]


async def list(
    endpoint_id: EndpointIDParameter,
    deployment_id: DeploymentIDParameter,
    limit: Annotated[Optional[int], Parameter(help="Maximum adapters to return")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List LoRA adapters attached to a beta endpoint deployment."""
    response = await show_loading_status(
        "Loading adapter attachments...",
        config.client.beta.endpoints.adapters.list(
            endpoint_id,
            deployment_id,
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    _print_adapters_table(response.data or [])
    _print_next_page(response.next_cursor, endpoint_id=endpoint_id, deployment_id=deployment_id)


async def add(
    endpoint_id: EndpointIDParameter,
    deployment_id: DeploymentIDParameter,
    adapter_model_id: AdapterModelIDParameter,
    *,
    adapter_revision_id: Annotated[
        Optional[str],
        Parameter(help="Adapter model revision ID to pin; defaults to latest"),
    ] = None,
    force: Annotated[bool, Parameter(help="Evict the oldest adapter if the deployment is at capacity")] = False,
    config: CLIConfigParameter,
) -> None:
    """Attach a LoRA adapter to a beta endpoint deployment."""
    response = await show_loading_status(
        "Adding adapter attachment...",
        config.client.beta.endpoints.adapters.create(
            endpoint_id=endpoint_id,
            deployment_id=deployment_id,
            adapter_model_id=adapter_model_id,
            adapter_revision_id=adapter_revision_id or omit,
            force=force or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]OK[/green] Adapter attached.")
    _print_adapter_detail(response)


async def retrieve(
    endpoint_id: EndpointIDParameter,
    deployment_id: DeploymentIDParameter,
    adapter_id: AdapterIDParameter,
    *,
    adapter_model_id: AdapterModelIDOption = None,
    config: CLIConfigParameter,
) -> None:
    """Get a beta endpoint adapter attachment by its dad_ ID."""
    response = await show_loading_status(
        "Loading adapter attachment...",
        config.client.beta.endpoints.adapters.retrieve(
            adapter_id,
            endpoint_id=endpoint_id,
            deployment_id=deployment_id,
            adapter_model_id=adapter_model_id or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    _print_adapter_detail(response)


async def update(
    endpoint_id: EndpointIDParameter,
    deployment_id: DeploymentIDParameter,
    adapter_id: AdapterIDParameter,
    *,
    adapter_revision_id: Annotated[str, Parameter(help="New adapter model revision ID to pin")],
    etag: Annotated[str, Parameter(help="ETag from a prior add, update, get, or list response")],
    adapter_model_id: AdapterModelIDOption = None,
    config: CLIConfigParameter,
) -> None:
    """Update the pinned revision for a beta endpoint adapter attachment."""
    response = await show_loading_status(
        "Updating adapter attachment...",
        config.client.beta.endpoints.adapters.update(
            adapter_id,
            endpoint_id=endpoint_id,
            deployment_id=deployment_id,
            adapter_revision_id=adapter_revision_id,
            etag=etag,
            adapter_model_id=adapter_model_id or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]OK[/green] Adapter updated.")
    _print_adapter_detail(response)


async def remove(
    endpoint_id: EndpointIDParameter,
    deployment_id: DeploymentIDParameter,
    adapter_id: AdapterIDParameter,
    *,
    etag: Annotated[str, Parameter(help="ETag from a prior add, update, get, or list response")],
    adapter_model_id: AdapterModelIDOption = None,
    config: CLIConfigParameter,
) -> None:
    """Remove a beta endpoint adapter attachment by its dad_ ID."""
    await show_loading_status(
        "Removing adapter attachment...",
        config.client.beta.endpoints.adapters.delete(
            adapter_id,
            endpoint_id=endpoint_id,
            deployment_id=deployment_id,
            etag=etag,
            adapter_model_id=adapter_model_id or omit,
        ),
    )

    if config.json:
        console.print_json("{}")
        return

    console.print(f"[green]OK[/green] Deleted adapter attachment {adapter_id}.")


def _print_adapters_table(adapters: list[Any]) -> None:
    table = ListTable("Adapter Attachments", empty_message="No adapter attachments found for this deployment")
    table.add_primary_column("Attachment ID", ratio=2)
    table.add_column("Model ID", ratio=2)
    table.add_column("Revision", ratio=2)
    table.add_column("State", width=8, no_wrap=True)
    table.add_column("Ready", width=5, no_wrap=True)
    table.add_column("ETag", ratio=2)

    for adapter in adapters:
        state, ready = _summarize_clusters(adapter.per_cluster or [])
        table.add_row(
            adapter.id,
            adapter.adapter_model_id,
            adapter.desired_revision_id,
            state,
            ready,
            adapter.etag,
        )

    console.print(table)


def _print_adapter_detail(adapter: Any) -> None:
    console.print(f"[dim][primary]Attachment ID:[/primary][/dim]\t{adapter.id}")
    console.print(f"[dim][primary]Model ID:[/primary][/dim]\t{adapter.adapter_model_id}")
    console.print(f"[dim][primary]Revision ID:[/primary][/dim]\t{adapter.desired_revision_id}")
    console.print(f"[dim][primary]ETag:[/primary][/dim]\t\t{adapter.etag}")

    if adapter.adapter_model:
        console.print(f"[dim][primary]Model:[/primary][/dim]\t\t{adapter.adapter_model}")
    if adapter.desired_revision:
        console.print(f"[dim][primary]Revision:[/primary][/dim]\t{adapter.desired_revision}")

    clusters = adapter.per_cluster or []
    if not clusters:
        return

    console.print("\nClusters")
    table = ListTable(show_lines=False)
    table.add_primary_column("Cluster ID", ratio=2)
    table.add_column("State")
    table.add_column("Ready")
    table.add_column("Revision", ratio=2)
    table.add_column("Reason", ratio=2)

    for cluster in clusters:
        table.add_row(
            cluster.cluster_id,
            _short_state(cluster.state),
            f"{cluster.ready_pod_count}/{cluster.total_pod_count}",
            cluster.realized_revision_id or "-",
            cluster.reason or cluster.message or "-",
        )

    console.print(table)


def _summarize_clusters(clusters: list[Any]) -> tuple[str, str]:
    if not clusters:
        return "-", "-"

    states = sorted({_short_state(cluster.state) for cluster in clusters})
    ready = sum(cluster.ready_pod_count for cluster in clusters)
    total = sum(cluster.total_pod_count for cluster in clusters)
    return ", ".join(states), f"{ready}/{total}"


def _short_state(state: str) -> str:
    return state.removeprefix("ADAPTER_LOAD_STATE_")


def _print_next_page(next_cursor: str | None, *, endpoint_id: str, deployment_id: str) -> None:
    if not next_cursor:
        return
    console.print("\n[blue dim]To display the next page, run:[/blue dim]")
    console.print(
        f"  [dim]-[/dim] [white]tg beta endpoints adapters list {endpoint_id} {deployment_id} "
        f"--after {next_cursor}[/white]"
    )
