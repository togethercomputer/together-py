from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Adapters")
async def list(
    *,
    config: CLIConfigParameter,
) -> None:
    """List all LoRA adapters bound to endpoints."""
    response = await config.client.endpoints.list_adapters()

    bindings = response.get("data", []) if isinstance(response, dict) else []

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    EMPTY_MESSAGE = "No adapters are bound to any endpoints.\nTo bind an adapter run:\n  [dim]-[/dim] [primary]tg endpoints adapters add BASE_MODEL ADAPTER_NAME[/primary]"
    table = ListTable("Adapters", empty_message=EMPTY_MESSAGE)
    table.add_primary_column("Adapter")
    table.add_column("Endpoint", ratio=2)

    for binding in bindings:
        table.add_row(binding.get("adapter_name", ""), binding.get("endpoint_name", ""))

    console.print(table)
