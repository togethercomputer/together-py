from __future__ import annotations

from typing import Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters.remediations._resolve_remediation import resolve_remediation


async def reject(
    remediation_id: str,
    comment: Annotated[Optional[str], Parameter(help="Comment explaining the rejection")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Reject a pending remediation."""
    remediation = await show_loading_status("Finding remediation...", resolve_remediation(config, remediation_id))
    response = await show_loading_status(
        "Rejecting remediation...",
        config.client.beta.clusters.remediations.reject(
            remediation_id,
            cluster_id=remediation.cluster_id,
            instance_id=remediation.instance_id,
            comment=comment or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[blue]Remediation rejected.[/blue] ({response.id})")
