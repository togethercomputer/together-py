from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def availability_zones(
    *,
    config: CLIConfigParameter,
) -> None:
    """List all availability zones."""

    avzones = await show_loading_status("Loading availability zones...", config.client.endpoints.list_avzones())
    if config.json:
        console.print_json(openapi_dumps(avzones).decode("utf-8"))
        return
    if not avzones or not avzones.avzones:
        console.print("No availability zones found")
        return
    console.print("Available zones:")
    for zone in sorted(avzones.avzones):
        console.print(f"  {zone}")
