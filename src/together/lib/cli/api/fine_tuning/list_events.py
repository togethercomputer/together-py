from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination


async def list_events(
    fine_tune_id: str,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List fine-tuning events."""
    response = await config.client.fine_tuning.list_events(fine_tune_id)
    response.data = response.data or []

    events, next_cursor = mock_pagination(response.data, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(events).decode("utf-8"))
        return

    table = ListTable()
    table.add_primary_column("Type")
    table.add_column("Message")
    table.add_column("Created At")

    for i in events:
        table.add_row(i.type, i.message, format_timestamp(i.created_at))

    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg fine-tuning list-events {fine_tune_id} --after {next_cursor}[/white]")
