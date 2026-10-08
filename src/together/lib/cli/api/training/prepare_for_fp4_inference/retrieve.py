from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump
from together.lib.cli.api.training.prepare_for_fp4_inference._utils import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    PollIntervalParameter,
    watch_job,
    report_job,
)


async def retrieve(
    job_id: Annotated[str, Parameter(help="FP4 preparation job ID (shp-quant-...)")],
    *,
    watch: Annotated[
        bool, Parameter(alias="-w", negative=(), help="Wait for the job to finish, printing status and events")
    ] = False,
    poll_interval: PollIntervalParameter = DEFAULT_POLL_INTERVAL_SECONDS,
    config: CLIConfigParameter,
) -> None:
    """Retrieve FP4 preparation job details."""
    if watch:
        job = await watch_job(job_id, config, poll_interval)
    else:
        job = await show_loading_status(
            "Retrieving FP4 preparation job...",
            config.client.post_training.prepare_for_fp4_inference.retrieve(job_id),
        )
        if not config.json:
            event_count = len(job.events)
            print_model_dump(job.model_copy(update={"events": None}), show_nulls=False)
            if event_count > 0:
                console.print(f"\n  [dim]Total events:[/dim] {event_count}")
                console.print(f"  [dim]To see the event log run[/dim] tg training fp4 list-events {job_id}")

    report_job(job, config)
