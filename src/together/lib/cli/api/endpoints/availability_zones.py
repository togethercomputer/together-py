from __future__ import annotations

from typing import Annotated

from rich import print
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def availability_zones(
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List all availability zones."""
    import sys

    avzones = await show_loading_status("Loading availability zones...", config.client.endpoints.list_avzones())
    if config.json:
        console.print_json(openapi_dumps(avzones).decode("utf-8"))
        return
    if not avzones or not avzones.avzones:
        print("No availability zones found", file=sys.stderr)
        return
    print("Available zones:", file=sys.stderr)
    for zone in sorted(avzones.avzones):
        print(f"  {zone}")
