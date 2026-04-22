from __future__ import annotations

import sys
from typing import Annotated

from cyclopts import Parameter, CoercionError

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status

NON_CANCELLABLE_STATES = ["cancel_requested", "cancelled", "error", "completed", "user_error"]


async def cancel(
    fine_tune_id: Annotated[str, Parameter(help="The ID of the fine-tuning job to cancel")],
    quiet: Annotated[bool, Parameter(negative="", show=False)] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Cancel fine-tuning job."""
    can_prompt = quiet is False and config.non_interactive is False
    if config.json and can_prompt:
        raise CoercionError("To use json mode, you must use --non-interactive")

    job = await show_loading_status("Retrieving fine-tuning job...", config.client.fine_tuning.retrieve(fine_tune_id))

    if job.status in NON_CANCELLABLE_STATES:
        console.print(
            f"[red]x[/red] Training is not currently cancellable.\n  Current status is [yellow]{job.status}[/yellow]",
        )
        sys.exit(1)

    if can_prompt:
        console.print("[yellow]You will be billed for any completed training steps upon cancellation.[/yellow]\n")
        confirm_response = input(f"Do you want to cancel job {fine_tune_id}? [y/N]")
        if "y" not in confirm_response.lower():
            if config.json:
                console.print_json('{"status": "Cancel not submitted"}')
            else:
                console.print("Cancel not submitted")
            return

    response = await show_loading_status(
        "Cancelling fine-tuning job...", config.client.fine_tuning.cancel(fine_tune_id)
    )
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]+[/green] Cancelled fine-tuning job")
