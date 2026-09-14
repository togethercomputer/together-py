from __future__ import annotations

import asyncio
from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def stop(
    endpoint_id: str,
    wait: Annotated[bool, Parameter(help="Wait for the endpoint to stop", negative=False)] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Stop a dedicated inference endpoint."""
    await show_loading_status("Stopping endpoint...", config.client.endpoints.update(endpoint_id, state="STOPPED"))

    if config.json:
        console.print_json(openapi_dumps({"message": "Successfully marked endpoint as stopping"}).decode("utf-8"))
        return

    if wait:
        console.print("[green]√[/green] Successfully requested endpoint to stop.")
        with console.status(
            "[progress.description]Waiting for endpoint to stop...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            while (await config.client.endpoints.retrieve(endpoint_id)).state != "STOPPED":
                await asyncio.sleep(1)
        console.print("[green]√[/green] Endpoint stopped")

    else:
        console.print("[green]√[/green] Endpoint is stopping.\n  This may take a few minutes.")
