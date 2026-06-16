from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.components.list import ListTable
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

EndpointIDParameter = Annotated[str, Parameter(help="The ID of the endpoint")]
ModelIDParameter = Annotated[
    str,
    Parameter(help='Combined identifier in format "endpoint_name:adapter_model_name"'),
]


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


@handle_endpoint_api_errors("Endpoint adapters")
async def add(
    endpoint_id: EndpointIDParameter,
    model_id: ModelIDParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """Bind a LoRA adapter model to a dedicated endpoint."""
    response = await show_loading_status(
        "Adding adapter...",
        config.client.endpoints.adapters.add(endpoint_id, model_id=model_id),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Adapter added.")
    if response.api_model_id:
        console.print(f"[dim][primary]Model ID:[/primary][/dim]\t{response.api_model_id}")


@handle_endpoint_api_errors("Endpoint adapters")
async def remove(
    endpoint_id: EndpointIDParameter,
    model_id: ModelIDParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """Remove a LoRA adapter binding from a dedicated endpoint."""
    response = await show_loading_status(
        "Removing adapter...",
        config.client.endpoints.adapters.remove(endpoint_id, model_id=model_id),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Adapter removed.")
    if response.api_model_id:
        console.print(f"[dim][primary]Model ID:[/primary][/dim]\t{response.api_model_id}")
