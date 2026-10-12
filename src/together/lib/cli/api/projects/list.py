from __future__ import annotations

from typing import Optional, Sequence
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.types.project import Project
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
    """List projects the current credentials can access."""
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

    print_project_list(
        response.data or [],
        current_id=config.client.project_id,
        next_cursor=response.next_cursor,
    )


def print_project_list(
    projects: Sequence[Project],
    *,
    current_id: str | None,
    next_cursor: str | None = None,
) -> None:
    """Same table `tg projects list` prints."""
    table = ListTable(
        "Projects",
        empty_message="No projects found.",
    )
    table.add_primary_column("ID")
    table.add_column("Name", ratio=2)
    table.add_column("Slug")
    table.add_column("Organization", ratio=2)

    for project in projects:
        table.add_row(
            project.id,
            _name_cell(project, current_id),
            project.slug,
            f"{project.organization_name} [dim]({project.organization_id})[/dim]",
        )
    console.print(table)

    if current_id is None and projects:
        console.print("\n[blue dim]To use a project, run:[/blue dim]")
        console.print("  [dim]-[/dim] [white]tg switch <project-id>[/white]")

    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg projects list --after {next_cursor}[/white]")


def _name_cell(project: Project, current_id: str | None) -> str:
    if current_id is not None and project.id == current_id:
        return f"{project.name} [dim](current)[/dim]"
    return project.name
