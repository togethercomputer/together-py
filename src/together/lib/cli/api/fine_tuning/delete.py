import json

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.option("--quiet", is_flag=True, help="Do not prompt for confirmation before deleting job")
@handle_api_errors("Fine-tuning")
def delete(ctx: click.Context, fine_tune_id: str, force: bool = False, quiet: bool = False) -> None:
    """Delete fine-tuning job"""
    client: Together = ctx.obj

    if not quiet:
        confirm_response = input(
            f"Are you sure you want to delete fine-tuning job {fine_tune_id}? This action cannot be undone. [y/N] "
        )
        if confirm_response.lower() != "y":
            click.echo("Deletion cancelled")
            return

    response = client.fine_tuning.delete(fine_tune_id, force=force)

    click.echo(json.dumps(response.model_dump(exclude_none=True), indent=4))
