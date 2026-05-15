from __future__ import annotations

from typing import Literal, Optional, Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters.remediations._util import (
    omit_if_none,
    parse_states,
    print_remediations,
)

OptionalRemediationModeParameter = Annotated[
    Optional[
        Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
        ]
    ],
    Parameter(help="Filter by remediation mode"),
]


async def list(
    cluster_id: str,
    instance_id: Annotated[Optional[str], Parameter(help="Instance ID to list remediations for")] = None,
    mode: OptionalRemediationModeParameter = None,
    state: Annotated[Optional[str], Parameter(help="Comma-separated remediation states to include")] = None,
    order_by: Annotated[Optional[str], Parameter(help="Order by expression")] = None,
    page_size: Annotated[Optional[int], Parameter(help="Maximum results to return")] = None,
    page_token: Annotated[Optional[str], Parameter(help="Pagination token from a previous request")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List node remediations for a cluster or instance."""
    response = await show_loading_status(
        "Loading remediations...",
        config.client.beta.clusters.remediations.list(
            instance_id or "-",
            cluster_id=cluster_id,
            mode=omit_if_none(mode),
            state=parse_states(state),
            order_by=omit_if_none(order_by),
            page_size=omit_if_none(page_size),
            page_token=omit_if_none(page_token),
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_remediations(response.remediations)
    if response.has_next and response.next_page_token:
        command = f"tg beta clusters remediations list {cluster_id}"
        if instance_id:
            command += f" {instance_id}"
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]{command} --page-token {response.next_page_token}[/white]")
