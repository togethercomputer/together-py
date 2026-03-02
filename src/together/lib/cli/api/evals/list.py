from __future__ import annotations

from typing import Any, List, Literal, TypeVar, Optional, Annotated, cast

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

status_colors = {
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "error": "red",
    "user_error": "red",
    "completed": "green",
}


async def list(
    status: Annotated[
        Optional[Literal["pending", "queued", "running", "completed", "error", "user_error"]],
        Parameter(help="Filter evals by status."),
    ] = None,
    limit: Annotated[Optional[int], Parameter(help="The number of evals to return.")] = None,
    after: Annotated[Optional[str], AfterParameter] = None,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List evals."""
    response = await show_loading_status(
        "Loading evals...", config.client.evals.list(status=status or omit, limit=limit or omit)
    )

    data, next_cursor = mock_pagination(response, cursor_field="workflow_id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(data).decode("utf-8"))
        return

    table = ListTable("Evals")
    table.add_primary_column("Workflow ID", ratio=2)
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Model")
    table.add_column("Model A")
    table.add_column("Model B")

    for job in data:
        model = deep_get(job.parameters, ["model_to_evaluate", "model"], "")
        model_a = deep_get(job.parameters, ["model_a", "model"], "")
        model_b = deep_get(job.parameters, ["model_b", "model"], "")
        status_color = status_colors[job.status] if job.status in status_colors else "white"
        table.add_row(
            f"[link=https://api.together.xyz/evaluations/result/{job.workflow_id}]{job.workflow_id}[/link]",
            job.type,
            f"[{status_color}]{job.status}[/{status_color}]",
            model,
            model_a,
            model_b,
        )
    console.print(table)
    if next_cursor:
        console.print(f"\n[dim]>[/dim] To display the next page, run `tg evals list --after {next_cursor}`")


T = TypeVar("T")


def deep_get(dictionary: dict[str, Any] | None, keys: List[str], default: T) -> T:
    cur = cast(Any, dictionary)
    for key in keys:
        if isinstance(cur, dict) and key in cur:
            cur = cast(Any, cur[key])
        else:
            return default
    return cast(T, cur)
