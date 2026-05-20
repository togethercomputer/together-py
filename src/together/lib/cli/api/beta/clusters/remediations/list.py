from __future__ import annotations

from typing import Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status


async def list(
    cluster_id: str,
    instance_id: Annotated[Optional[str], Parameter(help="Instance ID to list remediations for")] = None,
    after: Annotated[Optional[str], Parameter(help="Pagination token from a previous request")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List node remediations for a cluster or instance."""
    response = await show_loading_status(
        "Loading remediations...",
        config.client.beta.clusters.remediations.list(
            instance_id or "-",
            cluster_id=cluster_id,
            page_token=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable(title="Cluster Remediations", empty_message="No remediations found for this cluster.")
    table.add_column("Created")
    table.add_primary_column("Instance", ratio=3)
    table.add_column("Mode")
    table.add_column("State")
    table.add_column("Remediation ID", ratio=3)

    for remediation in response.remediations:
        table.add_row(
            format_datetime(remediation.create_time) if remediation.create_time else "-",
            _format_instance(remediation.instance_id, remediation.instance_name),
            remediation.mode.replace("REMEDIATION_MODE_", ""),
            _colorize(remediation.state),
            remediation.id,
        )

    console.print(table)
    if response.has_next and response.next_page_token:
        command = f"tg beta clusters remediations ls {cluster_id}"
        if instance_id:
            command += f" {instance_id}"
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]{command} --after {response.next_page_token}[/white]")


def _colorize(state: str) -> str:
    state_colors = {
        "PENDING_APPROVAL": "yellow",
        "PENDING": "yellow",
        "RUNNING": "yellow",
        "SUCCEEDED": "green",
        "FAILED": "red",
        "CANCELLED": "dim",
        "AUTO_RESOLVED": "green",
    }
    color = state_colors[state] if state in state_colors else "white"
    return f"[{color}]{state}[/{color}]"


def _format_instance(instance_id: str, instance_name: str | None) -> str:
    if not instance_name:
        return instance_id
    return f"{instance_name} ({instance_id})"
