from typing import Any, Dict, List
from datetime import datetime, timezone

import click
from tabulate import tabulate

from together import Together
from together.lib.utils import finetune_price_to_dollars
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.api._utils import handle_api_errors, generate_progress_text


@click.command()
@click.pass_context
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Fine-tuning")
def list(ctx: click.Context, json: bool) -> None:
    """List fine-tuning jobs"""
    client: Together = ctx.obj

    response = client.fine_tuning.list()

    response.data = response.data or []

    # Use a default datetime for None values to make sure the key function always returns a comparable value
    # Sort newest to oldest
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    if json:
        click.echo(openapi_dumps(response.data))
        return

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        price = finetune_price_to_dollars(float(str(i.total_price)))  # convert to string for mypy typing

        # Show the progress text if the job is running
        status = str(i.status)  # Convert to string for mypy typing
        status_color = status_colors[i.status] if i.status in status_colors else "white"
        if i.status == "running":
            status += f": {generate_progress_text(i, datetime.now(timezone.utc))}"

        display_list.append(
            {
                "ID": click.style(i.id, fg=status_color),
                "Base Model": click.style(i.model or "", fg=status_color),
                "Suffix": click.style(i.suffix or "", fg=status_color),
                "Status": click.style(status, fg=status_color),
                "Price": click.style(f"${price:,.2f}", fg=status_color),
                "Created At": click.style(format_datetime(i.created_at), fg=status_color),
            }
        )
    table = tabulate(display_list, headers="keys")

    click.echo(table)


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
