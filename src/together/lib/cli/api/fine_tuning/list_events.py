from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


async def list_events(
    fine_tune_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """List fine-tuning events."""
    response = await config.client.fine_tuning.list_events(fine_tune_id)
    events = response.data or []

    if config.json:
        console.print_json(openapi_dumps(events).decode("utf-8"))
        return

    table = ListTable(empty_message=f"No events found for job {fine_tune_id}")
    table.add_primary_column("Type")
    table.add_column("Message")
    table.add_column("Created At")

    for i in events:
        table.add_row(i.type, i.message, format_timestamp(i.created_at))

    console.print(table)
