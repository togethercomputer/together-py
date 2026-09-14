from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump
from together.lib.cli.api.beta.clusters.remediations._resolve_remediation import resolve_remediation


async def retrieve(
    remediation_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve remediation details."""
    remediation = await show_loading_status("Finding remediation...", resolve_remediation(config, remediation_id))
    response = await show_loading_status(
        "Retrieving remediation...",
        config.client.beta.clusters.remediations.retrieve(
            remediation_id,
            cluster_id=remediation.cluster_id,
            instance_id=remediation.instance_id,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_model_dump(response, show_nulls=False, only_set_fields=True)
