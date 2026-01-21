import json

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--quiet", is_flag=True, help="Do not prompt for confirmation before cancelling job")
@handle_api_errors("Fine-tuning")
def cancel(ctx: click.Context, fine_tune_id: str, quiet: bool = False) -> None:
    """Cancel fine-tuning job"""
    client: Together = ctx.obj
    if not quiet:
        confirm_response = input(
            "You will be billed for any completed training steps upon cancellation. "
            f"Do you want to cancel job {fine_tune_id}? [y/N]"
        )
        if "y" not in confirm_response.lower():
            click.echo({"status": "Cancel not submitted"})
            return
    response = client.fine_tuning.cancel(fine_tune_id)

    click.echo(json.dumps(response.model_dump(exclude_none=True), indent=4, default=datetime_serializer))
