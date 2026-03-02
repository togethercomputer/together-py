from __future__ import annotations

import json as json_lib
from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether

from together.types.beta.clusters import ClusterStorage


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


async def list_(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List storage volumes."""
    response = await client.beta.clusters.storage.list()
    if json_output:
        print(json_lib.dumps(response.model_dump(), indent=2))
    else:
        _print_storage(response.volumes)
