from __future__ import annotations

import sys
from typing import Literal, Optional, Annotated
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
    output: Annotated[
        Optional[Literal["json", "graph"]],
        Parameter(
            "--output",
            help="Override the output format. 'json' prints raw JSON, 'graph' renders ASCII plots. By default the format is chosen automatically based on whether stdout is a terminal.",
        ),
    ] = None,
) -> None:
    """Retrieve training metrics for a fine-tuning job."""

    if output != "json" and config.json:
        raise ValueError(
            f"--output {output!r} conflicts with --json. Either remove --json or set --output json."
        )
    output_json = output == "json" or config.json

    is_tty = sys.stdout.isatty()
    # Determine output format: explicit --output or --json flag takes priority, then auto-detect via isatty.
    # When stdout is redirected (e.g. > file.txt or | jq), is_tty is False and we fall back to raw JSON.
    show_plots = (output == "graph") if output else (is_tty and not output_json)

    resolution_value = resolution if not show_plots else console.width - METRICS_WIDTH_PADDING
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
        if not is_tty:
            # stdout is redirected — print raw JSON so it pipes cleanly
            sys.stdout.write(json_bytes.decode("utf-8") + "\n")
        else:
            console.print_json(json_bytes.decode("utf-8"))
        return

    if not metrics:
        console.print(f"[muted]No metrics found for job {fine_tune_id}[/muted]")
        return

    console.print(metrics_ascii_charts(metrics, width=console.width - METRICS_WIDTH_PADDING))
