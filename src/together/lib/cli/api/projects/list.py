from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter


async def list(
    limit: Annotated[Optional[int], Parameter(help="Maximum projects to return")] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List projects accessible to the authenticated caller."""
    response = await show_loading_status(
        "Loading projects...",
        config.client.projects.list(
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable("Projects", empty_message="No projects found.")
    table.add_primary_column("ID")
    table.add_column("Name", ratio=2)
    table.add_column("Slug")
    table.add_column("Organization", ratio=2)

    for project in response.data or []:
        table.add_row(
            project.id,
            project.name,
            project.slug,
            project.organization_name,
        )

    console.print(table)

    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg projects list --after {response.next_cursor}[/white]")
