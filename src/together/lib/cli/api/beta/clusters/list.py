from __future__ import annotations

from typing import Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination
from together.lib.cli.api.beta.clusters._util import print_clusters


async def list(
    after: AfterParameter = None,
    project_id: Annotated[Optional[str], Parameter(help="Project ID to filter clusters by")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List clusters."""
    response = await show_loading_status(
        "Loading clusters...",
        config.client.beta.clusters.list(project_id=project_id or omit),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode())
        return

    clusters, next_cursor = mock_pagination(response.clusters, cursor_field="cluster_id", cursor=after)

    print_clusters(clusters)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta clusters list --after {next_cursor}[/white]")
