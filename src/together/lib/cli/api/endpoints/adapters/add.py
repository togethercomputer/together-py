from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.cli.api.endpoints.adapters._parameters import ModelIDParameter, EndpointIDParameter


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
