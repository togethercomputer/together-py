from __future__ import annotations

import json as json_lib
from typing import Annotated, List

from cyclopts import Parameter
from tabulate import tabulate

from together import AsyncTogether

from together.types.beta.clusters import ClusterStorage


def _print_storage(storage_list: List[ClusterStorage]) -> None:
    data = []
    for v in storage_list:
        data.append({"ID": v.volume_id, "Name": v.volume_name, "Size": v.size_tib})
    print(tabulate(data, headers="keys", tablefmt="grid"))


async def delete(
    volume_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Delete a storage volume."""
    import sys

    if json_output:
        response = await client.beta.clusters.storage.delete(volume_id)
        print(json_lib.dumps(response.model_dump(), indent=2))
        return
    storage = await client.beta.clusters.storage.retrieve(volume_id)
    _print_storage([storage])
    resp = input(
        f"Clusters Storage: Are you sure you want to delete storage volume {storage.volume_name}? [y/N] "
    ).strip().lower()
    if resp != "y" and resp != "yes":
        return
    print("Clusters Storage: Deleting storage volume...", file=sys.stderr)
    await client.beta.clusters.storage.delete(volume_id)
    print(f"Clusters Storage: Deleted storage volume {storage.volume_name}", file=sys.stderr)
