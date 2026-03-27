import click
from rich import print, print_json

from together import Together
from together.lib.utils import convert_bytes, convert_unix_timestamp
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
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
def retrieve(ctx: click.Context, id: str, json: bool) -> None:
    """Retrieve file details"""

    client: Together = ctx.obj

    response = client.files.retrieve(id=id)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    # print(f"[bold]File details [/bold][dim white]({response.id})[/dim white]")
    print(f"[dim]Name[/dim]:    [white]{response.filename}[/white]")
    print(f"[dim]Size[/dim]:    [white]{convert_bytes(response.bytes)}[/white]")
    print(f"[dim]Type[/dim]:    [white]{response.file_type}[/white]")
    print(f"[dim]Purpose[/dim]: [white]{response.purpose}[/white]")
    print(f"[dim]Created[/dim]: [white]{format_timestamp(convert_unix_timestamp(response.created_at))}[/white]")
