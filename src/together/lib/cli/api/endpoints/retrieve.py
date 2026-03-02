from __future__ import annotations

from typing import Annotated

from rich import print_json
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import print_endpoint, handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def retrieve(
    endpoint_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Get a dedicated inference endpoint."""

    endpoint = await show_loading_status("Loading endpoint...", config.client.endpoints.retrieve(endpoint_id))
    if config.json:
        print_json(openapi_dumps(endpoint).decode("utf-8"))
        return

    print_endpoint(endpoint)
