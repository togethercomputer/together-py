from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def delete(
    id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Delete remote file"""
    response = await show_loading_status("Deleting file", config.client.files.delete(id))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[green]√[/green] File deleted")
