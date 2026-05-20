from __future__ import annotations

from typing import Optional, Annotated
from datetime import datetime

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.plot_finetune_metrics import METRICS_WIDTH_PADDING, metrics_ascii_charts


async def list_metrics(
    fine_tune_id: Annotated[str, Parameter(help="The ID of the fine-tuning job")],
    *,
    config: CLIConfigParameter,
    global_step_from: Annotated[
        Optional[int], Parameter(help="Filter metrics from this global step (inclusive).")
    ] = None,
    global_step_to: Annotated[Optional[int], Parameter(help="Filter metrics to this global step (inclusive).")] = None,
    logged_at_from: Annotated[
        Optional[datetime], Parameter(help="Filter metrics logged at or after this time.")
    ] = None,
    logged_at_to: Annotated[Optional[datetime], Parameter(help="Filter metrics logged at or before this time.")] = None,
    resolution: Annotated[
        Optional[int],
        Parameter(
            help="Number of uniformly sampled training metric points to return. Does not limit the number of eval metric points."
        ),
    ] = None,
) -> None:
    """Retrieve training metrics for a fine-tuning job."""
    response = await show_loading_status(
        "Fetching metrics...",
        config.client.fine_tuning.list_metrics(
            fine_tune_id,
            global_step_from=global_step_from if global_step_from is not None else omit,
            global_step_to=global_step_to if global_step_to is not None else omit,
            logged_at_from=logged_at_from if logged_at_from is not None else omit,
            logged_at_to=logged_at_to if logged_at_to is not None else omit,
            resolution=resolution if resolution is not None else omit,
        ),
    )

    metrics = response.metrics or []

    if config.json:
        json_bytes = openapi_dumps(metrics)
        console.print_json(json_bytes.decode("utf-8"))
        return

    if len(metrics) == 0:
        console.print(f"[muted]No metrics found for job {fine_tune_id}[/muted]")
        return

    console.print(metrics_ascii_charts(metrics, width=console.width - METRICS_WIDTH_PADDING))
