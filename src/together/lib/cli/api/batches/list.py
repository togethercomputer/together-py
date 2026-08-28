from __future__ import annotations

from datetime import datetime, timezone

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.batches._utils import STATUS_COLORS, format_endpoint
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination


async def list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List batch jobs."""
    response = await show_loading_status("Loading batch jobs...", config.client.batches.list())
    jobs = response or []

    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    jobs.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    jobs_to_display, next_cursor = mock_pagination(jobs, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(jobs_to_display).decode("utf-8"))
        return

    table = ListTable(
        empty_message="You don't have any batch jobs yet. To submit your first batch run:\n  [dim]-[/dim] [primary]tg batches submit[/primary]"
    )
    table.add_primary_column("ID")
    table.add_column("API")
    table.add_column("Model")
    table.add_column("Status")
    table.add_column("Created At")

    for job in jobs_to_display:
        status = str(job.status) if job.status is not None else ""
        status_color = STATUS_COLORS.get(status, "white")
        if job.status == "IN_PROGRESS" and job.progress is not None:
            status = f"{status}: {job.progress:g}%"

        table.add_row(
            job.id or "",
            format_endpoint(job.endpoint),
            job.x_model_id or "",
            f"[{status_color}]{status}[/{status_color}]",
            format_datetime(job.created_at) if job.created_at else "",
        )
    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg batches list --after {next_cursor}[/white]")
