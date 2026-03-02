from __future__ import annotations

import sys
from typing import Annotated

from rich import print, print_json
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig

NON_CANCELLABLE_STATES = ["cancel_requested", "cancelled", "error", "completed", "user_error"]


async def cancel(
    fine_tune_id: str,
    quiet: bool = False,  # deprecated in favor of --non-interactive
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Cancel fine-tuning job."""
    job = await config.client.fine_tuning.retrieve(fine_tune_id)

    # if config.json and not (quiet or config.non_interactive):
    #     raise MissingArgumentError("json", "To use json mode, you must use --quiet")

    if job.status in NON_CANCELLABLE_STATES:
        print(
            f"[red]Training is not currently cancellable.[/red]\n\nCurrent status is [yellow]{job.status}[/yellow]",
            file=sys.stderr,
        )
        sys.exit(1)

    if not quiet or not config.non_interactive:
        confirm_response = input(
            "You will be billed for any completed training steps upon cancellation. "
            f"Do you want to cancel job {fine_tune_id}? [y/N]"
        )
        if "y" not in confirm_response.lower():
            if config.json:
                print_json('{"status": "Cancel not submitted"}')
            else:
                print("Cancel not submitted")
            return

    response = await config.client.fine_tuning.cancel(fine_tune_id)
    if config.json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    print("Cancelled fine-tuning job")
