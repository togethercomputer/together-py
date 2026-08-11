from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import confirm
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters._util import print_clusters


async def delete(
    cluster_id: str,
    force: Annotated[bool, Parameter(negative=(), help="Delete without confirmation")] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Delete a cluster by ID."""

    if config.json:
        response = await config.client.beta.clusters.delete(cluster_id=cluster_id)
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    cluster_name: str | None = None
    if not config.non_interactive and not force:
        cluster = await show_loading_status("", config.client.beta.clusters.retrieve(cluster_id=cluster_id))
        cluster_name = cluster.cluster_name
        print_clusters([cluster])
        if not await confirm(f"Are you sure you want to delete cluster {cluster.cluster_name}?"):
            return

    await show_loading_status("Deleting cluster...", config.client.beta.clusters.delete(cluster_id))
    if cluster_name:
        console.print(f"Deleted {cluster_name} ({cluster_id})")
    else:
        console.print(f"Deleted cluster ({cluster_id})")
