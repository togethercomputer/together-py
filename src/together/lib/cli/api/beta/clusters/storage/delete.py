from __future__ import annotations

import json as json_lib
from typing import List, Annotated

from rich import print
from cyclopts import Parameter

from together.types.beta.clusters import ClusterStorage
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status


def _print_storage(storage_list: List[ClusterStorage]) -> None:
    table = ListTable()
    table.add_primary_column("ID")
    table.add_column("Name")
    table.add_column("Size")
    for v in storage_list:
        table.add_row(v.volume_id, v.volume_name, f"{v.size_tib} TiB")
    console.print(table)


async def delete(
    volume_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Delete a storage volume."""

    if config.json:
        response = await config.client.beta.clusters.storage.delete(volume_id)
        print(json_lib.dumps(response.model_dump(), indent=2))
        return

    storage = await show_loading_status("", config.client.beta.clusters.storage.retrieve(volume_id))
    _print_storage([storage])
    resp = (
        input(f"\nClusters Storage: Are you sure you want to delete storage volume {storage.volume_name}? [y/N] ")
        .strip()
        .lower()
    )

    if resp != "y" and resp != "yes":
        return

    await show_loading_status("Deleting cluster volume...", config.client.beta.clusters.storage.delete(volume_id))
    console.print(f"[blue]Deleted. ({volume_id})[/blue]")
