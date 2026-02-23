from __future__ import annotations

from rich import print_json

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    volume_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a storage volume."""

    request = config.client.beta.clusters.storage.retrieve(volume_id)

    if config.json:
        print_json(openapi_dumps(await request).decode("utf-8"))
        return

    storage = await show_loading_status("Retrieving storage volume...", request)
    console.print(f"[bold dim]Name   [/bold dim][blue]{storage.volume_name}[/blue]")
    console.print(f"[bold dim]ID     [/bold dim][blue]{storage.volume_id}[/blue]")
    console.print(f"[bold dim]Size   [/bold dim][blue]{storage.size_tib}tb[/blue]")
    console.print(f"[bold dim]Status [/bold dim][blue]{storage.status}[/blue]")
