from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status


async def list_events(
    job_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """List events for an FP4 preparation job."""
    response = await show_loading_status(
        "Loading events...", config.client.post_training.prepare_for_fp4_inference.list_events(job_id)
    )

    if config.json:
        console.print_json(openapi_dumps(response.data).decode("utf-8"))
        return

    table = ListTable(empty_message=f"No events found for job {job_id}")
    table.add_primary_column("Type")
    table.add_column("Level")
    table.add_column("Message")
    table.add_column("Created At")

    for event in response.data:
        table.add_row(event.type, event.level, event.message, format_datetime(event.created_at))

    console.print(table)
