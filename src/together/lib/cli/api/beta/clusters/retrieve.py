from __future__ import annotations

from typing import Annotated

from rich import print, print_json
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    cluster_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Retrieve a cluster by ID."""

    response = await show_loading_status("Retrieving cluster...", config.client.beta.clusters.retrieve(cluster_id))

    if config.json:
        print_json(openapi_dumps(response).decode("utf-8"))
    else:
        # TODO: Add a pretty print for the cluster
        print(response)
