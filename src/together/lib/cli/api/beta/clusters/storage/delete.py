from __future__ import annotations

from together._utils._json import openapi_dumps
from together.types.beta.clusters import ClusterStorage
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status


def _print_storage(storage: ClusterStorage) -> None:
    table = ListTable()
    table.add_primary_column("ID")
    table.add_column("Name")
    table.add_column("Size")
    table.add_row(storage.volume_id, storage.volume_name, f"{storage.size_tib} TiB")
    console.print(table)


async def delete(
    volume_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Delete a storage volume."""

    if config.json:
        response = await config.client.beta.clusters.storage.delete(volume_id)
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    storage = await show_loading_status("", config.client.beta.clusters.storage.retrieve(volume_id))
    _print_storage(storage)
    resp = (
        input(f"\nClusters Storage: Are you sure you want to delete storage volume {storage.volume_name}? [y/N] ")
        .strip()
        .lower()
    )

    if resp != "y" and resp != "yes":
        return

    await show_loading_status("Deleting cluster volume...", config.client.beta.clusters.storage.delete(volume_id))
    console.print(f"[blue]Deleted. ({volume_id})[/blue]")
