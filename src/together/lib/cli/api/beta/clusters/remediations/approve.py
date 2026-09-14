from __future__ import annotations

from typing import Literal, Optional, Annotated, cast

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters.remediations._resolve_remediation import resolve_remediation

RemediationModeParameter = Annotated[
    Literal[
        "VM_ONLY",
        "HOST_AWARE",
        "EVICT_WITHOUT_REPLACEMENT",
        "REBOOT_VM",
        "HOST_POWER_CYCLE",
    ],
    Parameter(help="Remediation mode to use after approval"),
]


async def approve(
    remediation_id: str,
    comment: Annotated[Optional[str], Parameter(help="Comment explaining the approval")] = None,
    *,
    mode: Optional[RemediationModeParameter] = None,
    config: CLIConfigParameter,
) -> None:
    """Approve a pending remediation."""
    safe_mode = (
        omit
        if mode is None
        else cast(
            Literal[
                "REMEDIATION_MODE_VM_ONLY",
                "REMEDIATION_MODE_HOST_AWARE",
                "REMEDIATION_MODE_EVICT_WITHOUT_REPLACEMENT",
                "REMEDIATION_MODE_REBOOT_VM",
                "REMEDIATION_MODE_HOST_POWER_CYCLE",
            ],
            f"REMEDIATION_MODE_{mode}",
        )
    )

    remediation = await show_loading_status("Finding remediation...", resolve_remediation(config, remediation_id))
    response = await show_loading_status(
        "Approving remediation...",
        config.client.beta.clusters.remediations.approve(
            remediation_id,
            cluster_id=remediation.cluster_id,
            instance_id=remediation.instance_id,
            comment=comment or omit,
            mode=safe_mode,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[blue]Remediation approved.[/blue] ({response.id})")
