from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training._params import CheckpointTypeName, checkpoint_type_query, require_positive_limit
from together.lib.cli.api.training._display import shell_arg, page_cursor, print_next_page, print_checkpoints_table
from together.lib.cli.utils._mock_pagination import AfterParameter


async def list_checkpoints(
    limit: Annotated[Optional[int], Parameter(help="Maximum checkpoints to return (1-100)")] = None,
    after: AfterParameter = None,
    checkpoint_type: Annotated[
        Optional[CheckpointTypeName],
        Parameter(name="--type", help="Only return training or inference checkpoints."),
    ] = None,
    session: Annotated[
        Optional[str],
        Parameter(name=("--session", "--session-id"), help="Only return checkpoints from this training session."),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List training and inference checkpoints."""
    require_positive_limit(limit)
    response = await show_loading_status(
        "Loading checkpoints...",
        config.client.post_training.checkpoints.list(
            limit=limit if limit is not None else omit,
            after=after or omit,
            session_id=session or omit,
            type=checkpoint_type_query(checkpoint_type),
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_checkpoints_table(response.data or [])
    cursor = page_cursor(response.meta)
    if cursor:
        print_next_page(
            _next_command(cursor, limit=limit, checkpoint_type=checkpoint_type, session=session)
        )


def _next_command(
    cursor: str,
    *,
    limit: int | None,
    checkpoint_type: CheckpointTypeName | None,
    session: str | None,
) -> str:
    parts = ["tg training ls-checkpoints"]
    if limit is not None:
        parts.append(f"--limit {limit}")
    if checkpoint_type:
        parts.append(f"--type {checkpoint_type}")
    if session:
        parts.append(f"--session {shell_arg(session)}")
    parts.append(f"--after {shell_arg(cursor)}")
    return " ".join(parts)
