from __future__ import annotations

import re
from typing import Literal, Optional, Annotated, AsyncIterator
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.types.endpoint_list_events_response import EndpointListEventsResponse
from together.lib.cli.api.endpoints._utils._resolve_model import resolve_endpoint

LevelInput = Literal["debug", "info", "warn", "warning", "error"]
SDKLevel = Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"]
LevelParameter = Annotated[
    Optional[LevelInput],
    Parameter(help="Minimum severity: debug, info, warn, or error. Omit to disable severity filtering."),
]
LEVEL_MAP: dict[LevelInput, SDKLevel] = {
    "debug": "LEVEL_DEBUG",
    "info": "LEVEL_INFO",
    "warn": "LEVEL_WARN",
    "warning": "LEVEL_WARN",
    "error": "LEVEL_ERROR",
}


def _short_name(fully_qualified_name: str) -> str:
    return fully_qualified_name.rsplit("/", 1)[-1]


# /projects/{project}/endpoints/{id}/events, with or without a /v2 prefix.
_ENDPOINT_EVENTS_PATH = re.compile(r"/projects/[^/]+/endpoints/[^/]+/events$")


def _event_type_values(types: str | None) -> list[str] | None:
    if not types:
        return None
    values = [part.strip() for part in types.split(",") if part.strip()]
    return values or None


def _repeat_endpoint_event_types(request: httpx.Request) -> None:
    """Split a comma-joined ``types`` value into repeated query keys.

    ``--types deployment.scaled,condition.set`` is the documented CLI form. The
    events API rejects that comma-joined value, and the generated client
    comma-joins every array. The shared query encoder stays unchanged; this
    rewrites the one request after that encoder has run.
    """
    if _ENDPOINT_EVENTS_PATH.search(request.url.path) is None:
        return

    expanded: list[tuple[str, str]] = []
    changed = False
    for key, value in request.url.params.multi_items():
        if key != "types":
            expanded.append((key, value))
            continue
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if parts == [value]:
            expanded.append((key, value))
            continue
        changed = True
        expanded.extend(("types", part) for part in parts)
    if changed:
        request.url = request.url.copy_with(params=expanded)


@asynccontextmanager
async def _repeat_event_type_query(http_client: httpx.AsyncClient) -> AsyncIterator[None]:
    async def _on_request(request: httpx.Request) -> None:
        _repeat_endpoint_event_types(request)

    hooks = http_client.event_hooks.setdefault("request", [])
    hooks.append(_on_request)
    try:
        yield
    finally:
        hooks.remove(_on_request)


def _format_event_datetime(value: datetime) -> str:
    local = value.astimezone() if value.tzinfo is not None else value
    return local.strftime("%m/%d/%y %I:%M%p")


def _format_message(event: EndpointListEventsResponse) -> str:
    text = escape_rich_markup(event.message or event.log_excerpt or "")
    if event.level == "LEVEL_ERROR":
        return f"[error]{text}[/error]"
    if event.level == "LEVEL_WARN":
        return f"[warning]{text}[/warning]"
    return text


def _source_label(
    event: EndpointListEventsResponse,
    *,
    deployment_names: dict[str, str],
    endpoint_name: str,
) -> str:
    if event.deployment_id:
        if event.deployment_id in deployment_names:
            return deployment_names[event.deployment_id]
        if event.name:
            return _short_name(event.name)
        return event.deployment_id
    if endpoint_name:
        return endpoint_name
    if event.name:
        return _short_name(event.name)
    return event.endpoint_id


async def events(
    id: Annotated[str, Parameter(help="Endpoint ID or name")],
    *,
    deployment_ids: Annotated[
        Optional[str],
        Parameter(help="Deployment IDs whose events should be included. Comma-separated list."),
    ] = None,
    min_level: LevelParameter = None,
    types: Annotated[
        Optional[str],
        Parameter(help="Event types to include, such as deployment.scaled or condition.set. Comma-separated list."),
    ] = None,
    subject_id: Annotated[
        Optional[str],
        Parameter(help="ID of a subject associated with the event, such as a rollout."),
    ] = None,
    since: Annotated[Optional[datetime], Parameter(help="Return only events at or after this time.")] = None,
    until: Annotated[Optional[datetime], Parameter(help="Return only events strictly before this time.")] = None,
    limit: Annotated[
        Optional[int],
        Parameter(help="Maximum number of events to return. Max 10000, defaults to 50."),
    ] = None,
    after: AfterParameter = None,
    config: CLIConfigParameter,
) -> None:
    """List endpoint audit and lifecycle events."""
    endpoint = await show_loading_status("Resolving endpoint...", resolve_endpoint(config, id))

    async with _repeat_event_type_query(config.client._client):
        response = await show_loading_status(
            "Loading endpoint events...",
            config.client.endpoints.list_events(
                endpoint.id,
                after=after or omit,
                deployment_ids=deployment_ids.split(",") if deployment_ids else omit,
                limit=limit if limit is not None else omit,
                min_level=LEVEL_MAP[min_level] if min_level else omit,
                since=since if since is not None else omit,
                subject_id=subject_id or omit,
                types=_event_type_values(types) or omit,
                until=until if until is not None else omit,
            ),
        )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    deployment_names: dict[str, str] = {}
    endpoint_name = _short_name(endpoint.name)
    for deployment in endpoint.deployments or []:
        deployment_names[deployment.id] = _short_name(deployment.name)

    events = response.data or []
    for event in events:
        if event.deployment_id and event.name and event.deployment_id not in deployment_names:
            deployment_names[event.deployment_id] = _short_name(event.name)

    table = ListTable(empty_message=f"No events found for endpoint {endpoint.id}.")
    table.add_column("Created", width=16, no_wrap=True)
    table.add_primary_column("Type", ratio=2)
    table.add_column("Source", ratio=2, no_wrap=True)
    table.add_column("Message", ratio=3)

    for event in events:
        table.add_row(
            _format_event_datetime(event.created_at),
            event.type,
            _source_label(event, deployment_names=deployment_names, endpoint_name=endpoint_name),
            _format_message(event),
        )

    console.print(table)
    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg endpoints events {endpoint.id} --after {response.next_cursor}[/white]")
