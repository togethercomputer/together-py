from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training._params import SessionStatusName, session_status_query, require_positive_limit
from together.lib.cli.api.training._display import shell_arg, page_cursor, print_next_page, print_sessions_table
from together.lib.cli.utils._mock_pagination import AfterParameter


async def list_sessions(
    limit: Annotated[Optional[int], Parameter(help="Maximum sessions to return (1-100)")] = None,
    after: AfterParameter = None,
    created_by: Annotated[
        Optional[str],
        Parameter(help='Filter by creator ID. Pass "me" for sessions you created.'),
    ] = None,
    model_resources_id: Annotated[
        Optional[str],
        Parameter(name=("--resources", "--model-resources-id"), help="Filter by model resource ID"),
    ] = None,
    status: Annotated[
        Optional[list[SessionStatusName]],
        Parameter(help="Filter by status. Repeat to include more than one."),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List training sessions."""
    require_positive_limit(limit)
    response = await show_loading_status(
        "Loading training sessions...",
        config.client.beta.rl.sessions.list(
            limit=limit if limit is not None else omit,
            after=after or omit,
            created_by=created_by or omit,
            model_resources_id=model_resources_id or omit,
            status=session_status_query(status),
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_sessions_table(response.data or [])
    cursor = page_cursor(response.meta)
    if cursor:
        print_next_page(
            _next_command(
                cursor,
                limit=limit,
                created_by=created_by,
                model_resources_id=model_resources_id,
                status=status,
            )
        )


def _next_command(
    cursor: str,
    *,
    limit: int | None,
    created_by: str | None,
    model_resources_id: str | None,
    status: list[SessionStatusName] | None,
) -> str:
    parts = ["tg training ls-sessions"]
    if limit is not None:
        parts.append(f"--limit {limit}")
    if created_by:
        parts.append(f"--created-by {shell_arg(created_by)}")
    if model_resources_id:
        parts.append(f"--resources {shell_arg(model_resources_id)}")
    for value in status or []:
        parts.append(f"--status {value}")
    parts.append(f"--after {shell_arg(cursor)}")
    return " ".join(parts)
