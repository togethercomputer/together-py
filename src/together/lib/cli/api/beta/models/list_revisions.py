from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status

_VALIDATION_STATUS = {
    "REVISION_VALIDATION_STATUS_PENDING": "[yellow]Pending[/yellow]",
    "REVISION_VALIDATION_STATUS_SUCCESS": "[green]Success[/green]",
    "REVISION_VALIDATION_STATUS_FAILED": "[red]Failed[/red]",
    "REVISION_VALIDATION_STATUS_ERROR": "[red]Error[/red]",
}


def format_validation_status(status: str | None) -> str:
    if not status:
        return ""
    return _VALIDATION_STATUS.get(status, status)


async def list_revisions(
    id: Annotated[str, Parameter(help="Model ID (ml_...) whose immutable revisions should be listed")],
    *,
    config: CLIConfigParameter,
) -> None:
    response = await show_loading_status("Loading model revisions...", config.client.beta.models.list_revisions(id))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable("Revisions", empty_message="No revisions found.")
    table.add_primary_column("Revision ID", ratio=2)
    table.add_column("Validation")
    table.add_column("Last Validated")
    table.add_column("Created At")
    for revision in response.data or []:
        table.add_row(
            revision.revision_id or "",
            format_validation_status(revision.validation_status),
            format_datetime(revision.last_validated_at) if revision.last_validated_at else "",
            format_datetime(revision.created_at) if revision.created_at else "",
        )
    console.print()
    console.print(table)
