from __future__ import annotations

from typing import Literal, Optional, Annotated, cast

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status

RemediationModeParameter = Annotated[
    Literal[
        "VM_ONLY",
        "HOST_AWARE",
        "EVICT_WITHOUT_REPLACEMENT",
        "REBOOT_VM",
        "HOST_POWER_CYCLE",
    ],
    Parameter(help="The type of remediation to perform"),
]


async def create(
    cluster_id: Annotated[str, Parameter(help="The ID of the cluster")],
    instance_id: Annotated[str, Parameter(help="The ID of the node within the cluster to remediate")],
    *,
    mode: RemediationModeParameter,
    remediation_id: Annotated[Optional[str], Parameter(help="Client-specified ID for idempotency")] = None,
    reason: Annotated[Optional[str], Parameter(help="Reason for the remediation")] = None,
    config: CLIConfigParameter,
) -> None:
    """Create a node remediation for an instance."""
    safe_mode = cast(
        Literal[
            "REMEDIATION_MODE_VM_ONLY",
            "REMEDIATION_MODE_HOST_AWARE",
            "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
            "REMEDIATION_MODE_REBOOT_VM",
            "REMEDIATION_MODE_HOST_POWER_CYCLE",
        ],
        f"REMEDIATION_MODE_{mode}",
    )

    response = await show_loading_status(
        "Creating remediation...",
        config.client.beta.clusters.remediations.create(
            instance_id,
            cluster_id=cluster_id,
            mode=safe_mode,
            remediation_id=remediation_id or omit,
            reason=reason or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[green]√ Remediation created[/green] [dim]({response.id})[/dim]")
    console.print(f"  Remediations may take some time to complete.\n")
    console.print(f"  To retrieve the status:")
    console.print(f"    [dim]-[/dim] [primary]tg beta clusters remediations {response.id}[/primary]")
