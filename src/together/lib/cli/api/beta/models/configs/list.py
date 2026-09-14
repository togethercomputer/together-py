from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_configs_table
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.lib.cli.api.beta.endpoints._utils._resolve_model import resolve_model_reference


async def list(
    model: Annotated[
        str,
        Parameter(help="Model ID, resource path, or name to filter configs for", required=True),
    ],
    *,
    limit: Annotated[Optional[int], Parameter(help="Maximum configs to return")] = None,
    after: AfterParameter = None,
    config: CLIConfigParameter,
) -> None:
    """List beta model configs usable by endpoint deployments."""
    reference = await resolve_model_reference(config, model)
    response = await show_loading_status(
        "Loading model configs...",
        config.client.beta.models.configs.list(
            reference_model=reference.reference_model or omit,
            reference_model_id=reference.reference_model_id or omit,
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_configs_table(response.data or [], empty_message="No model configs found.")
    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta models configs {model} --after {response.next_cursor}[/white]")
