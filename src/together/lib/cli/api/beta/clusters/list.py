from __future__ import annotations

from typing import Annotated

from rich import print_json
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.api.beta.clusters._util import print_clusters


async def list(
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List clusters."""
    response = await config.client.beta.clusters.list()
    if config.json:
        print_json(openapi_dumps(response).decode())
    else:
        print_clusters(response.clusters)
