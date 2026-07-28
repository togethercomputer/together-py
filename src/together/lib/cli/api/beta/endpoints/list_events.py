from __future__ import annotations

from typing import Literal, Optional, Annotated
from datetime import datetime

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter

LevelParameter = Annotated[
    Optional[Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"]],
    Parameter(help="Minimum severity. Omit to disable severity filtering."),
]
SourceKindsParameter = Annotated[
    Optional[list[Literal["SOURCE_KIND_ENDPOINT", "SOURCE_KIND_DEPLOYMENT"]]],
    Parameter(help="Resource kinds whose events should be included. Can be used multiple times."),
]


async def list_events(
    endpoint_id: Annotated[str, Parameter(help="Endpoint ID")],
    after: AfterParameter = None,
    deployment_ids: Annotated[
        Optional[list[str]],
        Parameter(help="Deployment IDs whose events should be included. Can be used multiple times."),
    ] = None,
    limit: Annotated[
        Optional[int],
        Parameter(help="Maximum number of events to return. Max 10000, defaults to 50."),
    ] = None,
    min_level: LevelParameter = None,
    since: Annotated[Optional[datetime], Parameter(help="Return only events at or after this time.")] = None,
    source_kinds: SourceKindsParameter = None,
    subject_id: Annotated[
        Optional[str],
        Parameter(help="ID of a subject associated with the event, such as a rollout."),
    ] = None,
    types: Annotated[
        Optional[list[str]],
        Parameter(help="Event types to include, such as deployment.scaled or condition.set. Can be used multiple times."),
    ] = None,
    until: Annotated[Optional[datetime], Parameter(help="Return only events strictly before this time.")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List endpoint audit and lifecycle events."""
    response = await show_loading_status(
        "Loading endpoint events...",
        config.client.beta.endpoints.list_events(
            endpoint_id,
            after=after or omit,
            deployment_ids=deployment_ids or omit,
            limit=limit if limit is not None else omit,
            min_level=min_level or omit,
            since=since if since is not None else omit,
            source_kinds=source_kinds or omit,
            subject_id=subject_id or omit,
            types=types or omit,
            until=until if until is not None else omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    events = response.data or []
    table = ListTable(empty_message=f"No events found for endpoint {endpoint_id}.")
    table.add_column("Created")
    table.add_column("Level")
    table.add_primary_column("Type", ratio=2)
    table.add_column("Source")
    table.add_column("Subject", ratio=2)
    table.add_column("Message", ratio=3)

    for event in events:
        table.add_row(
            format_datetime(event.created_at),
            event.level.replace("LEVEL_", ""),
            event.type,
            event.source_kind.replace("SOURCE_KIND_", ""),
            event.subject_id or event.deployment_id or event.endpoint_id,
            event.message or event.log_excerpt or "",
        )

    console.print(table)
    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta endpoints list-events {endpoint_id} --after {response.next_cursor}[/white]")
