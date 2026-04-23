from __future__ import annotations

from typing import Literal, Optional, Annotated, cast

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.types.dedicated_endpoint import DedicatedEndpoint
from together.lib.cli.api.endpoints._utils import colorized_endpoint_state, handle_endpoint_api_errors
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination


@handle_endpoint_api_errors("Endpoints")
async def list(
    _type: Annotated[
        Optional[Literal["dedicated", "serverless"]],
        Parameter(name="--type", help="Deprecated and no longer has any effect."),
    ] = None,
    _mine: Annotated[Optional[bool], Parameter(name="--mine", help="Deprecated and no longer has any effect.")] = None,
    usage_type: Annotated[
        Optional[Literal["on-demand", "reserved"]], Parameter(help="Filter by usage type options")
    ] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List all inference endpoints (includes both dedicated and serverless endpoints)."""
    endpoints = await config.client.endpoints.list(
        type="dedicated",
        mine=True,
        usage_type=usage_type or omit,
    )

    sorted_endpoints = sorted(endpoints.data, key=lambda x: x.created_at, reverse=True)
    endpoints_to_display, next_cursor = mock_pagination(sorted_endpoints, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(endpoints_to_display).decode("utf-8"))
        return

    if len(endpoints_to_display) == 0:
        console.print("No dedicated endpoints found")
        return

    table = ListTable("Endpoints")
    table.add_primary_column("ID")
    table.add_column("Name", ratio=2)
    table.add_column("State")
    # show_autoscaling = mine is True
    for endpoint in endpoints_to_display:
        id_with_link = f"[link={f'https://api.together.ai/endpoints/{endpoint.name}'}]{endpoint.id}[/link]"
        table.add_row(id_with_link, endpoint.name, colorized_endpoint_state(cast(DedicatedEndpoint, endpoint)))

    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg endpoints list --after {next_cursor}[/white]")
