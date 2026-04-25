from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

EMPTY_MESSAGE = "You don't have any storage volumes yet. To create your first storage volume run:\n  [dim]-[/dim] [primary]tg beta clusters storage create[/primary]"


async def list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List storage volumes."""
    response = await show_loading_status("Loading storage volumes...", config.client.beta.clusters.storage.list())

    data, next_cursor = mock_pagination(response.volumes, cursor_field="volume_id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable(title="Cluster Storage", empty_message=EMPTY_MESSAGE)
    table.add_primary_column("ID")
    table.add_column("Name")
    table.add_column("Size")
    for volume in data:
        table.add_row(volume.volume_id, volume.volume_name, f"{volume.size_tib} TiB")
    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta clusters storage list --after {next_cursor}[/white]")
