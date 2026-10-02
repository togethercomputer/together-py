from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.types.beta.rl.session import Session
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.rl._params import SessionStatusName, session_status_query, require_positive_limit
from together.lib.cli.api.beta.rl._display import shell_arg, print_next_page, print_checkpoints_table
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.types.beta.rl.inference_checkpoint import InferenceCheckpoint

# Inference checkpoints are stored on the training session. The checkpoints
# list endpoint returns training checkpoints only, so this command pages
# through sessions and flattens `inference_checkpoints`.
_DEFAULT_LIMIT = 100
_SESSION_PAGE_SIZE = 100
_MAX_SESSION_PAGES = 100


@dataclass
class _CheckpointPage:
    rows: list[tuple[str, InferenceCheckpoint]]
    next_cursor: str | None
    cursor_found: bool


async def list_checkpoints(
    limit: Annotated[Optional[int], Parameter(help="Maximum inference checkpoints to return")] = None,
    after: AfterParameter = None,
    session: Annotated[
        Optional[str],
        Parameter(
            name=("--session", "--session-id"),
            help="Training session ID. When set, only that session is loaded and other session filters are ignored.",
        ),
    ] = None,
    created_by: Annotated[
        Optional[str],
        Parameter(help='Only scan sessions created by this ID. Pass "me" for your sessions.'),
    ] = None,
    model_resources_id: Annotated[
        Optional[str],
        Parameter(
            name=("--resources", "--model-resources-id"),
            help="Only scan sessions on this model resource",
        ),
    ] = None,
    status: Annotated[
        Optional[list[SessionStatusName]],
        Parameter(help="Only scan sessions in these statuses. Repeat to include more than one."),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List inference checkpoints saved on training sessions."""
    require_positive_limit(limit)
    page = await show_loading_status(
        "Loading inference checkpoints...",
        _collect(
            config,
            limit=limit if limit is not None else _DEFAULT_LIMIT,
            after=after,
            session=session,
            created_by=created_by,
            model_resources_id=model_resources_id,
            status=status,
        ),
    )

    if config.json:
        console.print_json(
            openapi_dumps(
                {
                    "data": [
                        {**checkpoint.to_dict(mode="json", use_api_names=True), "session_id": session_id}
                        for session_id, checkpoint in page.rows
                    ],
                    "meta": {
                        "has_more": page.next_cursor is not None,
                        "limit": limit if limit is not None else _DEFAULT_LIMIT,
                        "next_cursor": page.next_cursor,
                    },
                }
            ).decode("utf-8")
        )
        return

    if after and not page.cursor_found:
        console.print(
            f"[yellow]![/yellow] Checkpoint {escape_rich_markup(after)} was not found while scanning training sessions."
        )
    print_checkpoints_table(page.rows)
    if page.next_cursor:
        print_next_page(
            _next_command(
                page.next_cursor,
                limit=limit,
                session=session,
                created_by=created_by,
                model_resources_id=model_resources_id,
                status=status,
            )
        )


async def _collect(
    config: CLIConfig,
    *,
    limit: int,
    after: str | None,
    session: str | None,
    created_by: str | None,
    model_resources_id: str | None,
    status: list[SessionStatusName] | None,
) -> _CheckpointPage:
    if session:
        loaded = await config.client.beta.rl.sessions.retrieve(session)
        return _slice(
            [(loaded.id, checkpoint) for checkpoint in loaded.inference_checkpoints], after=after, limit=limit
        )

    rows: list[tuple[str, InferenceCheckpoint]] = []
    found_after = after is None
    session_cursor: str | None = None
    seen_cursors: set[str] = set()
    truncated = False
    pages = 0
    while len(rows) <= limit:
        if pages >= _MAX_SESSION_PAGES:
            truncated = True
            break
        pages += 1
        page = await config.client.beta.rl.sessions.list(
            after=session_cursor or omit,
            limit=_SESSION_PAGE_SIZE,
            created_by=created_by or omit,
            model_resources_id=model_resources_id or omit,
            status=session_status_query(status),
        )
        for item in page.data or []:
            found_after = _take_checkpoints(item, rows, after=after, found_after=found_after, limit=limit)
            if len(rows) > limit:
                break
        if len(rows) > limit:
            break
        next_session = _session_cursor(page.meta)
        if next_session is None or next_session in seen_cursors or not (page.data or []):
            break
        seen_cursors.add(next_session)
        session_cursor = next_session

    if after is not None and not found_after:
        return _CheckpointPage(rows=[], next_cursor=None, cursor_found=False)

    has_more = len(rows) > limit or (truncated and bool(rows))
    visible = rows[:limit]
    next_cursor = visible[-1][1].id if has_more and visible else None
    return _CheckpointPage(rows=visible, next_cursor=next_cursor, cursor_found=True)


def _take_checkpoints(
    session: Session,
    rows: list[tuple[str, InferenceCheckpoint]],
    *,
    after: str | None,
    found_after: bool,
    limit: int,
) -> bool:
    for checkpoint in session.inference_checkpoints:
        if not found_after:
            if checkpoint.id == after:
                found_after = True
            continue
        rows.append((session.id, checkpoint))
        if len(rows) > limit:
            break
    return found_after


def _slice(
    rows: list[tuple[str, InferenceCheckpoint]],
    *,
    after: str | None,
    limit: int,
) -> _CheckpointPage:
    start = 0
    if after is not None:
        for index, (_session_id, checkpoint) in enumerate(rows):
            if checkpoint.id == after:
                start = index + 1
                break
        else:
            return _CheckpointPage(rows=[], next_cursor=None, cursor_found=False)
    visible = rows[start : start + limit]
    has_more = start + limit < len(rows)
    next_cursor = visible[-1][1].id if has_more and visible else None
    return _CheckpointPage(rows=visible, next_cursor=next_cursor, cursor_found=True)


def _session_cursor(meta: object) -> str | None:
    if meta is None:
        return None
    has_more = getattr(meta, "has_more", None)
    cursor = getattr(meta, "next_cursor", None)
    if has_more is False or not isinstance(cursor, str) or not cursor:
        return None
    return cursor


def _next_command(
    cursor: str,
    *,
    limit: int | None,
    session: str | None,
    created_by: str | None,
    model_resources_id: str | None,
    status: list[SessionStatusName] | None,
) -> str:
    parts = ["tg beta rl ls-checkpoints"]
    if limit is not None:
        parts.append(f"--limit {limit}")
    if session:
        parts.append(f"--session {shell_arg(session)}")
    elif created_by or model_resources_id or status:
        if created_by:
            parts.append(f"--created-by {shell_arg(created_by)}")
        if model_resources_id:
            parts.append(f"--resources {shell_arg(model_resources_id)}")
        for value in status or []:
            parts.append(f"--status {value}")
    parts.append(f"--after {shell_arg(cursor)}")
    return " ".join(parts)
