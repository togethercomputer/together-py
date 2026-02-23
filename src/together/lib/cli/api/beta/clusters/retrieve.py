from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    cluster_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a cluster by ID."""

    response = await show_loading_status("Retrieving cluster...", config.client.beta.clusters.retrieve(cluster_id))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
    else:
        # TODO: Add a pretty print for the cluster
        console.print(response)
