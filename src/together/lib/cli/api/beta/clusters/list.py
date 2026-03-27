import json as json_lib

import click

from together import Together
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
@auto_track_command
def list(ctx: click.Context, json: bool) -> None:
    """List clusters"""
    client: Together = ctx.obj

    response = client.beta.clusters.list()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        ctx.obj.print_clusters(response.clusters)
