from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.cli.api.endpoints.adapters._parameters import EndpointIDParameter


@handle_endpoint_api_errors("Endpoint adapters")
async def list(
    endpoint_id: EndpointIDParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """List LoRA adapters bound to a dedicated endpoint."""
    response = await show_loading_status(
        "Loading adapters...",
        config.client.endpoints.adapters.list(endpoint_id),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable("Endpoint Adapters", empty_message="No adapters found for this endpoint")
    table.add_primary_column("Model ID", ratio=2)
    table.add_column("Adapter Name")
    table.add_column("Endpoint Name")

    for adapter in response.data or []:
        table.add_row(adapter.api_model_id or "", adapter.adapter_name or "", adapter.endpoint_name or "")

    console.print(table)
