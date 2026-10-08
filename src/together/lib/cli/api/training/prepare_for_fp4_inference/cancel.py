from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._prompt import confirm as prompt_confirm
from together.lib.cli.utils._console import console
from together.lib.cli.utils._json_mode import exit_with_message
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training.prepare_for_fp4_inference._utils import NON_CANCELLABLE_STATUSES


async def cancel(
    job_id: Annotated[str, Parameter(help="The ID of the FP4 preparation job to cancel")],
    *,
    force: Annotated[bool, Parameter(alias="-y", negative=(), help="Skip the confirmation prompt")] = False,
    config: CLIConfigParameter,
) -> None:
    """Cancel an FP4 preparation job."""
    job = await show_loading_status(
        "Retrieving FP4 preparation job...", config.client.post_training.prepare_for_fp4_inference.retrieve(job_id)
    )
    if job.status in NON_CANCELLABLE_STATUSES:
        exit_with_message(
            f"[red]x[/red] Job is not currently cancellable.\n  Current status is [yellow]{job.status}[/yellow]",
            error=f"Job is not currently cancellable. Current status is {job.status}.",
            diagnostic=f"FP4 preparation job is not cancellable ({job.status})",
        )

    if not force and not config.non_interactive and not config.json:
        if not await prompt_confirm(f"Do you want to cancel job {job_id}?"):
            console.print("Cancel not submitted")
            return

    response = await show_loading_status(
        "Cancelling FP4 preparation job...", config.client.post_training.prepare_for_fp4_inference.cancel(job_id)
    )
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[green]+[/green] Cancellation requested for job {job_id}")
