from __future__ import annotations

from datetime import datetime

from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import generate_progress_bar
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.types.fine_tuning import COMPLETED_STATUSES
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump

_NEST_INDENT = 4


async def retrieve(
    fine_tune_id: str,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve fine-tuning job details."""
    response = await show_loading_status(
        "Retrieving fine-tuning job...", config.client.fine_tuning.retrieve(fine_tune_id)
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    event_count = len(response.events) if response.events else 0
    response.events = None

    if response.status not in COMPLETED_STATUSES:
        progress_text = generate_progress_bar(response, datetime.now().astimezone(), use_rich=True)
        console.print(progress_text)

    print_model_dump(response, show_nulls=False)
    if event_count > 0:
        console.print("\n[dim]FT Events:[/dim]")
        console.print(f"  [dim]Total events:[/dim] {event_count}")
        console.print(f"  [dim]To see event log data run[/dim] tg fine-tuning list-events {fine_tune_id}")
