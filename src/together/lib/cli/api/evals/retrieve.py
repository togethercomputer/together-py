from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    evaluation_id: Annotated[str, Parameter(help="The ID of the evaluation job")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Get details of a specific evaluation job."""
    response = await show_loading_status("Retrieving eval...", config.client.evals.retrieve(evaluation_id))
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    wid = response.workflow_id or evaluation_id
    console.print(
        f"[dim]Eval[/dim] [bold]{escape_rich_markup(str(wid))}[/bold] — "
        f"[dim]status[/dim] [bold]{escape_rich_markup(str(response.status))}[/bold] — "
        f"[dim]type[/dim] [bold]{escape_rich_markup(str(response.type))}[/bold]"
    )
