from __future__ import annotations

from typing import Annotated
from datetime import datetime

from cyclopts import Parameter

from together._types import Omit, omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils.plot_finetune_metrics import METRICS_WIDTH_PADDING, metrics_ascii_charts


async def list_metrics(
    fine_tune_id: Annotated[str, Parameter(help="The ID of the fine-tuning job")],
    *,
    config: CLIConfigParameter,
    global_step_from: Annotated[int | Omit, Parameter(help="Filter metrics from this global step (inclusive).")] = omit,
    global_step_to: Annotated[int | Omit, Parameter(help="Filter metrics to this global step (inclusive).")] = omit,
    logged_at_from: Annotated[datetime | Omit, Parameter(help="Filter metrics logged at or after this time.")] = omit,
    logged_at_to: Annotated[datetime | Omit, Parameter(help="Filter metrics logged at or before this time.")] = omit,
    resolution: Annotated[int | Omit, Parameter(help="Number of data points to return (used for JSON output).")] = omit,
) -> None:
    """Retrieve training metrics for a fine-tuning job."""

    if config.json:
        response = await show_loading_status(
            "Fetching metrics...",
            config.client.fine_tuning.list_metrics(
                fine_tune_id,
                global_step_from=global_step_from,
                global_step_to=global_step_to,
                logged_at_from=logged_at_from,
                logged_at_to=logged_at_to,
                resolution=resolution,
            ),
        )
        console.print_json(openapi_dumps(response.metrics or []).decode("utf-8"))
        return

    # For the ASCII chart always fetch at terminal width resolution for best fidelity.
    response = await show_loading_status(
        "Fetching metrics...",
        config.client.fine_tuning.list_metrics(
            fine_tune_id,
            global_step_from=global_step_from,
            global_step_to=global_step_to,
            logged_at_from=logged_at_from,
            logged_at_to=logged_at_to,
            resolution=console.width - METRICS_WIDTH_PADDING,
        ),
    )
    metrics = response.metrics or []

    if not metrics:
        console.print(f"[muted]No metrics found for job {fine_tune_id}[/muted]")
        return

    console.print(metrics_ascii_charts(metrics, width=console.width - METRICS_WIDTH_PADDING))
