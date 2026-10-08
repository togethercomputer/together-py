from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import confirm as prompt_confirm
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training.prepare_for_fp4_inference._utils import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    PollIntervalParameter,
    AdapterRevisionParameter,
    CalibrationFileParameter,
    watch_job,
    report_job,
    build_inputs,
    format_estimate,
    format_credit_warning,
    resolve_calibration_file,
)

_CONFIRMATION_MESSAGE = """You are about to merge adapter [bold]{adapter}[/bold] into its base model and prepare the result for FP4 inference.
{calibration_line}{price_line}
{warning}"""


async def create(
    adapter_object_id: Annotated[str, Parameter(help="Model object ID of the fine-tuned adapter to prepare")],
    *,
    adapter_revision_id: AdapterRevisionParameter = None,
    calibration_file: CalibrationFileParameter = None,
    confirm: Annotated[
        bool, Parameter(alias="-y", negative=(), help="Whether to skip the launch confirmation message")
    ] = False,
    watch: Annotated[
        bool, Parameter(alias="-w", negative=(), help="Wait for the job to finish, printing status and events")
    ] = False,
    poll_interval: PollIntervalParameter = DEFAULT_POLL_INTERVAL_SECONDS,
    config: CLIConfigParameter,
) -> None:
    """Prepare a fine-tuned adapter for FP4 inference."""
    calibration_file_id = await resolve_calibration_file(calibration_file, config)
    inputs = build_inputs(adapter_object_id, adapter_revision_id, calibration_file_id)

    estimate = await show_loading_status(
        "Estimating price...",
        config.client.post_training.prepare_for_fp4_inference.estimate_cost(inputs=inputs),
    )

    if not confirm and not config.json:
        calibration_line = (
            f"Calibration file: [bold]{calibration_file_id}[/bold]\n" if calibration_file_id is not None else ""
        )
        console.print(
            _CONFIRMATION_MESSAGE.format(
                adapter=adapter_object_id,
                calibration_line=calibration_line,
                price_line=format_estimate(estimate),
                warning=f"{format_credit_warning(estimate)}\n" if not estimate.allowed_to_proceed else "",
            )
        )
        if not config.non_interactive and not await prompt_confirm("Do you want to proceed?"):
            return

    job = await show_loading_status(
        "Creating FP4 preparation job...",
        config.client.post_training.prepare_for_fp4_inference.create(inputs=inputs),
    )
    if not config.json:
        console.print(f"[green]√ FP4 preparation job has been submitted.[/green] [dim]({job.id})[/dim]")

    if watch:
        job = await watch_job(job.id, config, poll_interval)

    report_job(job, config)
