from __future__ import annotations

from rich import print_json

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import print_endpoint, handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def retrieve(
    endpoint_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Get a dedicated inference endpoint."""

    endpoint = await show_loading_status("Loading endpoint...", config.client.endpoints.retrieve(endpoint_id))
    if config.json:
        print_json(openapi_dumps(endpoint).decode("utf-8"))
        return

    print_endpoint(endpoint)
