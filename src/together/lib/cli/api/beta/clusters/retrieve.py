import json as json_lib

import click
from rich import print

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def retrieve(ctx: click.Context, cluster_id: str, json: bool) -> None:
    """Retrieve a cluster by ID"""
    client: Together = ctx.obj

    if not json:
        click.echo(f"Clusters: Retrieving cluster...")

    response = client.beta.clusters.retrieve(cluster_id)

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        print(response)
