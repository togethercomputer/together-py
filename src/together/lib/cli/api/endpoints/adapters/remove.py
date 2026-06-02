from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors

BaseModelParameter = Annotated[str, Parameter(help="The dedicated endpoint name")]
AdapterNameParameter = Annotated[str, Parameter(help="The LoRA adapter model name to remove")]


@handle_endpoint_api_errors("Adapters")
async def remove(
    base_model: BaseModelParameter,
    adapter_name: AdapterNameParameter,
    *,
    config: CLIConfigParameter,
) -> None:
    """Remove a LoRA adapter from a dedicated endpoint."""
    response = await show_loading_status(
        "Removing adapter...",
        config.client.endpoints.delete_adapter(
            base_model=base_model,
            adapter_name=adapter_name,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Adapter removed from endpoint")
