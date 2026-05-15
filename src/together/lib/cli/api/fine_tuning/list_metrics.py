from __future__ import annotations

from typing import Annotated
from datetime import datetime

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.plot_finetune_metrics import METRICS_WIDTH_PADDING, metrics_ascii_charts


async def list_metrics(
    fine_tune_id: Annotated[str, Parameter(help="The ID of the fine-tuning job")],
    *,
    config: CLIConfigParameter,
    global_step_from: Annotated[int | None, Parameter(help="Filter metrics from this global step (inclusive).")] = None,
    global_step_to: Annotated[int | None, Parameter(help="Filter metrics to this global step (inclusive).")] = None,
    logged_at_from: Annotated[datetime | None, Parameter(help="Filter metrics logged at or after this time.")] = None,
    logged_at_to: Annotated[datetime | None, Parameter(help="Filter metrics logged at or before this time.")] = None,
    resolution: Annotated[int | None, Parameter(help="Number of training metric points to return. Does not limit the number of eval metric points.")] = None,
) -> None:
    """Retrieve training metrics for a fine-tuning job."""

    resolution_value = console.width - METRICS_WIDTH_PADDING if not config.json else resolution
    response = await show_loading_status(
        "Fetching metrics...",
        config.client.fine_tuning.list_metrics(
            fine_tune_id,
            global_step_from=global_step_from,
            global_step_to=global_step_to,
            logged_at_from=logged_at_from,
            logged_at_to=logged_at_to,
            resolution=resolution_value,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response.metrics or []).decode("utf-8"))
        return

    metrics = response.metrics or []

    if not metrics:
        console.print(f"[muted]No metrics found for job {fine_tune_id}[/muted]")
        return

    console.print(metrics_ascii_charts(metrics, width=console.width - METRICS_WIDTH_PADDING))
