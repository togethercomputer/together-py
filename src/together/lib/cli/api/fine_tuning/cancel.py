import sys

import click
from rich import print, print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors

NON_CANCELLABLE_STATES = ["cancel_requested", "cancelled", "error", "completed", "user_error"]


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--quiet", is_flag=True, help="Do not prompt for confirmation before cancelling job")
@click.option("--json", is_flag=True, help="Print output in JSON format, must use --force to use this option")
@handle_api_errors("Fine-tuning")
@auto_track_command
def cancel(ctx: click.Context, fine_tune_id: str, quiet: bool = False, json: bool = False) -> None:
    """Cancel fine-tuning job"""
    client: Together = ctx.obj
    job = client.fine_tuning.retrieve(fine_tune_id)

    if json and not quiet:
        raise click.BadOptionUsage("json", "To use json mode, you must use --quiet")

    if job.status in NON_CANCELLABLE_STATES:
        click.echo(
            click.style(f"Fine-tuning: ", fg="blue")
            + f"Training is not currently cancellable. Current status is "
            + click.style(job.status, fg="yellow"),
            file=sys.stderr if json else None,
        )
        return

    if not quiet:
        confirm_response = input(
            "You will be billed for any completed training steps upon cancellation. "
            f"Do you want to cancel job {fine_tune_id}? [y/N]"
        )
        if "y" not in confirm_response.lower():
            if json:
                print_json('{"status": "Cancel not submitted"}')
            else:
                click.echo("Cancel not submitted")
            return

    response = client.fine_tuning.cancel(fine_tune_id)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    print("Cancelled fine-tuning job")
