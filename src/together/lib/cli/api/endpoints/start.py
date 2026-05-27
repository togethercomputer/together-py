from __future__ import annotations

import asyncio
from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def start(
    endpoint_id: Annotated[
        str,
        Parameter(required=True, help="The ID of the endpoint to start"),
    ],
    wait: Annotated[bool, Parameter(help="Wait for the endpoint to start", negative=False)] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Start a dedicated inference endpoint."""
    response = await show_loading_status(
        "Starting endpoint...", config.client.endpoints.update(endpoint_id, state="STARTED")
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    if wait:
        console.print("[green]√[/green] Successfully requested endpoint to start.")
        with console.status(
            "[progress.description]Waiting for endpoint to start...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            while (await config.client.endpoints.retrieve(endpoint_id)).state != "STARTED":
                await asyncio.sleep(1)
        console.print("[green]√[/green] Endpoint started")
    else:
        console.print("[green]√[/green] Endpoint is starting.\n  This may take a few minutes.")
