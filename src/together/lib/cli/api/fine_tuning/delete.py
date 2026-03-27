import click
from rich import print, print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.option("--quiet", is_flag=True, help="Deprecated, use --force instead")
@click.option("--json", is_flag=True, help="Print output in JSON format, must use --force to use this option")
@handle_api_errors("Fine-tuning")
@auto_track_command
def delete(ctx: click.Context, fine_tune_id: str, force: bool = False, quiet: bool = False, json: bool = False) -> None:
    """Delete fine-tuning job"""
    client: Together = ctx.obj

    skip_confirmation = force or quiet

    if not skip_confirmation:
        if json:
            raise click.BadOptionUsage("json", "To use json mode, you must use --force")

        confirm_response = input(
            f"Are you sure you want to delete fine-tuning job {fine_tune_id}? This action cannot be undone. [y/N] "
        )
        if confirm_response.lower() != "y":
            click.echo("Deletion cancelled")
            return

    response = client.fine_tuning.delete(fine_tune_id)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    print(f"Deleted fine-tuning job")
