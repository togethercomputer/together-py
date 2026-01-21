import json

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("id", type=str, required=True)
@handle_api_errors("Files")
def retrieve(ctx: click.Context, id: str) -> None:
    """Upload file"""

    client: Together = ctx.obj

    response = client.files.retrieve(id=id)

    click.echo(json.dumps(response.model_dump(exclude_none=True), indent=4))
