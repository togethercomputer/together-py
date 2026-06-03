from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

EndpointIDParameter = Annotated[str, Parameter(help="The dedicated endpoint ID")]


@handle_endpoint_api_errors("Adapters")
async def list(
    endpoint_id: EndpointIDParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """List LoRA adapters bound to a dedicated endpoint."""
    response = await config.client.endpoints.list_adapters(endpoint_id=endpoint_id)

    bindings = response.get("data", []) if isinstance(response, dict) else []

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    EMPTY_MESSAGE = "No adapters are bound to this endpoint.\nTo add an adapter run:\n  [dim]-[/dim] [primary]tg endpoints adapters add ENDPOINT_ID MODEL_ID[/primary]"
    table = ListTable("Adapters", empty_message=EMPTY_MESSAGE)
    table.add_primary_column("Adapter")
    table.add_column("Endpoint", ratio=2)

    for binding in bindings:
        table.add_row(binding.get("adapter_name", ""), binding.get("endpoint_name", ""))

    console.print(table)
