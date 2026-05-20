from __future__ import annotations

import sys
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
    force_plots: Annotated[
        bool,
        Parameter(
            "--force-plots",
            help="Force rendering ASCII plots even when stdout is not a terminal (e.g. when redirecting output to a file).",
        ),
    ] = False,
) -> None:
    """Retrieve training metrics for a fine-tuning job."""

    is_tty = sys.stdout.isatty()
    # Show plots only when writing to a real terminal (or --force-plots is set) and --json wasn't requested.
    # When stdout is redirected (e.g. > file.txt or | jq), is_tty is False and we fall back to raw JSON.
    show_plots = (is_tty or force_plots) and not config.json

    resolution_value = resolution if resolution else console.width - METRICS_WIDTH_PADDING
    response = await show_loading_status(
        "Fetching metrics...",
        config.client.fine_tuning.list_metrics(
            fine_tune_id,
            global_step_from=global_step_from or omit,
            global_step_to=global_step_to or omit,
            logged_at_from=logged_at_from or omit,
            logged_at_to=logged_at_to or omit,
            resolution=resolution_value or omit,
        ),
    )

    metrics = response.metrics or []

    if not show_plots:
        json_bytes = openapi_dumps(metrics)
        if config.json:
            console.print_json(json_bytes.decode("utf-8"))
        else:
            # stdout is redirected — print raw JSON so it pipes cleanly
            sys.stdout.write(json_bytes.decode("utf-8") + "\n")
        return

    if not metrics:
        console.print(f"[muted]No metrics found for job {fine_tune_id}[/muted]")
        return

    console.print(metrics_ascii_charts(metrics, width=console.width - METRICS_WIDTH_PADDING))
