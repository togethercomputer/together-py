from __future__ import annotations

import sys
from typing import Optional, Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def delete(
    fine_tune_id: str,
    force: Annotated[Optional[bool], Parameter(negative="", help="Force deletion without confirmation")] = False,
    quiet: Annotated[Optional[bool], Parameter(negative="", help="Deprecated, use --force instead", show=False)] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Delete fine-tuning job."""
    skip_confirmation = force or quiet or config.non_interactive

    if not skip_confirmation:
        if config.json:
            console.print(
                "[red]To use --json option, you must also use --non-interactive option to bypass confirmation prompt[/red]"
            )
            console.print(f"\n[dim]>[/dim] tg fine-tuning delete {fine_tune_id} --json --non-interactive")
            sys.exit(1)
        confirm_response = input(
            f"Are you sure you want to delete fine-tuning job {fine_tune_id}? This action cannot be undone. [y/N] "
        )
        if confirm_response.lower() != "y":
            console.print("Deletion cancelled")
            return

    response = await show_loading_status("Deleting fine-tuning job...", config.client.fine_tuning.delete(fine_tune_id))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"Deleted fine-tuning job")
