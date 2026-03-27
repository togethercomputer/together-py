import click
from rich import print, print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("id", type=str, required=True)
@click.option(
    "--json",
    is_flag=True,
    help="Output the response in JSON format",
)
@handle_api_errors("Files")
@auto_track_command
def delete(ctx: click.Context, id: str, json: bool) -> None:
    """Delete remote file"""

    client: Together = ctx.obj

    response = client.files.delete(id=id)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    print(f"[green]File {id} deleted[/green]")
