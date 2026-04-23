from __future__ import annotations

from together.lib.utils import convert_bytes, convert_unix_timestamp
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve file metadata."""
    response = await show_loading_status("Retrieving file", config.client.files.retrieve(id))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[primary]Retrieved file details[/primary]")
    console.print(f"[bold dim]Id:[/bold dim]      [white]{response.id}[/white]")
    console.print(f"[bold dim]Name:[/bold dim]    [white]{response.filename}[/white]")
    console.print(f"[bold dim]Size:[/bold dim]    [white]{convert_bytes(response.bytes)}[/white]")
    console.print(f"[bold dim]Type:[/bold dim]    [white]{response.file_type}[/white]")
    console.print(f"[bold dim]Purpose:[/bold dim] [white]{response.purpose}[/white]")
    console.print(
        f"[bold dim]Created:[/bold dim] [white]{format_timestamp(convert_unix_timestamp(response.created_at))}[/white]"
    )
