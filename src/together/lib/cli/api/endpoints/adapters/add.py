from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

EndpointIDParameter = Annotated[str, Parameter(help="The dedicated endpoint ID")]
ModelIDParameter = Annotated[str, Parameter(help="Model ID in endpoint_name:adapter_name format")]


@handle_endpoint_api_errors("Adapters")
async def add(
    endpoint_id: EndpointIDParameter,
    model_id: ModelIDParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """Add a LoRA adapter to a dedicated endpoint."""
    response = await show_loading_status(
        "Adding adapter...",
        config.client.endpoints.add_adapter(
            endpoint_id=endpoint_id,
            model_id=model_id,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Adapter added to endpoint")
    console.print(f"[dim][primary]Endpoint:[/primary][/dim]\t{endpoint_id}")
    console.print(f"[dim][primary]Model ID:[/primary][/dim]\t{model_id}")
