from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_models_table
from together.lib.cli.utils._mock_pagination import AfterParameter


async def list(
    limit: Annotated[Optional[int], Parameter(help="Maximum models to return")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    response = await show_loading_status(
        "Loading beta models...",
        config.client.beta.models.list(
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_models_table(
        response.data or [],
        empty_message=(
            "No beta models found. To create one run:\n"
            "  [dim]-[/dim] [primary]tg beta models create --project-id <project> --model '<json>'[/primary]"
        ),
    )
    next_token = response.next_cursor if response.next_cursor else None
    if next_token:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta models ls --after {next_token}[/white]")
