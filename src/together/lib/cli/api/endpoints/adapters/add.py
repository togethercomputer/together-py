from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

BaseModelParameter = Annotated[str, Parameter(help="The dedicated endpoint name serving the base model")]
AdapterNameParameter = Annotated[str, Parameter(help="The LoRA adapter model name to add")]


@handle_endpoint_api_errors("Adapters")
async def add(
    base_model: BaseModelParameter,
    adapter_name: AdapterNameParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """Add a LoRA adapter to a dedicated endpoint."""
    response = await show_loading_status(
        "Adding adapter...",
        config.client.endpoints.set_lora_adapter(
            base_model=base_model,
            adapter_name=adapter_name,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Adapter added to endpoint")
    console.print(f"[dim][primary]Endpoint:[/primary][/dim]\t{base_model}")
    console.print(f"[dim][primary]Adapter:[/primary][/dim]\t{adapter_name}")
