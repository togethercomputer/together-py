from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def delete(
    endpoint_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Delete a dedicated inference endpoint."""
    await show_loading_status("Deleting endpoint...", config.client.endpoints.delete(endpoint_id))

    if config.json:
        console.print_json(openapi_dumps({"message": "Successfully deleted endpoint"}).decode("utf-8"))
        return

    console.print("[green]√[/green] Endpoint deleted")
