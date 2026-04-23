from __future__ import annotations

from datetime import datetime, timezone

from rich import print_json

from together.lib.utils import finetune_price_to_dollars
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.api._utils import generate_progress_text
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

status_colors = {
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "compressing": "yellow",
    "uploading": "yellow",
    "cancel_requested": "yellow",
    "cancelled": "red",
    "error": "red",
    "user_error": "red",
    "completed": "green",
}


async def list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List fine-tuning jobs."""
    response = await show_loading_status("Loading fine-tuning jobs...", config.client.fine_tuning.list())

    response.data = response.data or []

    # Use a default datetime for None values to make sure the key function always returns a comparable value
    # Sort newest to oldest
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    fine_tunings_to_display, next_cursor = mock_pagination(response.data, cursor_field="id", cursor=after)

    if config.json:
        print_json(openapi_dumps(fine_tunings_to_display).decode("utf-8"))
        return

    table = ListTable()
    table.add_primary_column("ID")
    table.add_column("Base Model")
    table.add_column("Suffix")
    table.add_column("Status")
    table.add_column("Price")
    table.add_column("Created At")

    for i in fine_tunings_to_display:
        price = finetune_price_to_dollars(float(str(i.total_price)))  # convert to string for mypy typing

        # Show the progress text if the job is running
        status = str(i.status)  # Convert to string for mypy typing
        status_color = status_colors[i.status] if i.status in status_colors else "white"
        if i.status == "running":
            status += f": {generate_progress_text(i, datetime.now(timezone.utc))}"

        table.add_row(
            i.id,
            i.model or "",
            i.suffix or "",
            f"[{status_color}]{status}[/{status_color}]",
            f"${price:,.2f}",
            format_datetime(i.created_at),
        )
    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg fine-tuning list --after {next_cursor}[/white]")
