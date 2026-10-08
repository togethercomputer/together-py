from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination
from together.lib.cli.api.training.prepare_for_fp4_inference._utils import format_status


async def list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List FP4 preparation jobs."""
    response = await show_loading_status(
        "Loading FP4 preparation jobs...", config.client.post_training.prepare_for_fp4_inference.list()
    )
    jobs = sorted(response.data, key=lambda job: job.created_at, reverse=True)
    jobs_to_display, next_cursor = mock_pagination(jobs, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(jobs_to_display).decode("utf-8"))
        return

    table = ListTable(
        empty_message="You don't have any FP4 preparation jobs yet. To start one run:\n  [dim]-[/dim] [primary]tg training fp4 create <adapter-object-id>[/primary]"
    )
    table.add_primary_column("ID")
    table.add_column("Adapter")
    table.add_column("Status")
    table.add_column("Prepared Model")
    table.add_column("Created At")

    for job in jobs_to_display:
        prepared_model = job.results.api_model_object_id if job.results is not None else None
        table.add_row(
            job.id,
            job.params.configuration.adapter_model_name,
            format_status(job.status),
            prepared_model or "",
            format_datetime(job.created_at),
        )
    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg training fp4 list --after {next_cursor}[/white]")
