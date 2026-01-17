import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("id", type=str, required=True)
@click.option("--output", type=str, default=None, help="Output filename")
@handle_api_errors("Files")
def retrieve_content(ctx: click.Context, id: str, output: str) -> None:
    """Retrieve file content and output to file"""

    client: Together = ctx.obj

    response = client.files.content(id=id)

    if output:
        with open(output, "wb") as f:
            f.write(response.read())
        click.echo(f"File saved to {output}")

    else:
        click.echo(response.read().decode("utf-8"))
