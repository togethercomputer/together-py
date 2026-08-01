from __future__ import annotations

from typing import Annotated
from datetime import datetime

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import generate_progress_bar
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.types.fine_tuning import COMPLETED_STATUSES
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump
from together.lib.cli.components.plot_finetune_metrics import METRICS_WIDTH_PADDING, metrics_block_sparklines

_NEST_INDENT = 4


async def retrieve(
    fine_tune_id: str,
    *,
    config: CLIConfigParameter,
    no_plots: Annotated[bool, Parameter(help="Print training metric sparklines.", negative=())] = False,
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

    if not no_plots:
        metrics_response = await show_loading_status(
            "Fetching metrics...",
            config.client.fine_tuning.list_metrics(fine_tune_id, resolution=console.width - METRICS_WIDTH_PADDING),
        )
        metrics = metrics_response.metrics or []

        if metrics:
            console.print("\n[muted]Training metrics:[/muted]")
            console.print(metrics_block_sparklines(metrics, width=console.width - METRICS_WIDTH_PADDING))

    if event_count > 0:
        console.print("\n[dim]FT Events:[/dim]")
        console.print(f"  [dim]Total events:[/dim] {event_count}")
        console.print(f"  [dim]To see event log data run[/dim] tg fine-tuning list-events {fine_tune_id}")
