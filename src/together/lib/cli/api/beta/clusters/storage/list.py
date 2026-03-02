from __future__ import annotations

from typing import Any, Dict, List, Annotated

from rich import print, print_json
from cyclopts import Parameter
from tabulate import tabulate

from together._utils._json import openapi_dumps
from together.types.beta.clusters import ClusterStorage
from together.lib.cli.utils.config import CLIConfig


def _print_storage(storage_list: List[ClusterStorage]) -> None:
    data: List[Dict[str, Any]] = []
    for volume in storage_list:
        data.append(
            {
                "ID": volume.volume_id,
                "Name": volume.volume_name,
                "Size": volume.size_tib,
            }
        )
    print(tabulate(data, headers="keys", tablefmt="grid"))


async def list(
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List storage volumes."""
    response = await config.client.beta.clusters.storage.list()
    if config.json:
        print_json(openapi_dumps(response).decode())
    else:
        _print_storage(response.volumes)
