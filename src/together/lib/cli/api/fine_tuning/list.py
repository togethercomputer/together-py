from datetime import datetime, timezone

import click
import typer
from rich.console import Console
from rich.table import Table

from together import Together
from together.lib.utils import finetune_price_to_dollars
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.api._utils import generate_progress_text

def list(
    ctx: typer.Context,
    json: bool = typer.Option(False, "--json", help="Output in JSON format")
) -> None:
    """List fine-tuning jobs"""
    client: Together = ctx.obj

    response = client.fine_tuning.list()
    response.data = response.data or []

    # Use a default datetime for None values to make sure the key function always returns a comparable value
    # Sort newest to oldest
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    if json:
        print(openapi_dumps(response.data))
        return

    console = Console()
    table = Table()
    table.add_column("ID")
    table.add_column("Base Model")
    table.add_column("Suffix")
    table.add_column("Status")
    table.add_column("Price")
    table.add_column("Created At")

    for i in response.data:
        price = finetune_price_to_dollars(float(str(i.total_price)))  # convert to string for mypy typing

        # Show the progress text if the job is running
        status = str(i.status)  # Convert to string for mypy typing
        status_color = status_colors[i.status] if i.status in status_colors else "white"
        if i.status == "running":
            status += f": {generate_progress_text(i, datetime.now(timezone.utc))}"

        table.add_row(
            click.style(i.id, fg=status_color),
            click.style(i.model or "", fg=status_color),
            click.style(i.suffix or "", fg=status_color),
            click.style(status, fg=status_color),
            click.style(f"${price:,.2f}", fg=status_color),
            click.style(format_datetime(i.created_at), fg=status_color),
        )
    console.print(table)


status_colors = {
    # Active status are yellow
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "compressing": "yellow",
    "uploading": "yellow",
    "cancel_requested": "yellow",
    # Bad ending states are red
    "cancelled": "red",
    "error": "red",
    "user_error": "red",
    # good ending states are green
    "completed": "green",
}
