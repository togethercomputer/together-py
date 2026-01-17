import json as json_lib

import click

from together import Together


@click.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
def list(ctx: click.Context, json: bool) -> None:
    """List clusters"""
    client: Together = ctx.obj

    response = client.beta.clusters.list()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        ctx.obj.print_clusters(response.clusters)
