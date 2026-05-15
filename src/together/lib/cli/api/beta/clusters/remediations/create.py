from __future__ import annotations

from typing import Literal, Optional, Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters.remediations._util import omit_if_none

RemediationModeParameter = Annotated[
    Literal[
        "REMEDIATION_MODE_VM_ONLY",
        "REMEDIATION_MODE_HOST_AWARE",
        "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
        "REMEDIATION_MODE_REBOOT_VM",
    ],
    Parameter(help="How the remediation should be performed"),
]


async def create(
    cluster_id: str,
    instance_id: str,
    *,
    mode: RemediationModeParameter,
    remediation_id: Annotated[Optional[str], Parameter(help="Client-specified ID for idempotency")] = None,
    reason: Annotated[Optional[str], Parameter(help="Reason for the remediation")] = None,
    config: CLIConfigParameter,
) -> None:
    """Create a node remediation for an instance."""
    request = config.client.beta.clusters.remediations.create(
        instance_id,
        cluster_id=cluster_id,
        mode=mode,
        remediation_id=omit_if_none(remediation_id),
        reason=omit_if_none(reason),
    )

    response = await show_loading_status("Creating remediation...", request)
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[blue]Remediation created successfully[/blue]")
    console.print(f"[primary]Remediation ID:[/primary] {response.id}")
