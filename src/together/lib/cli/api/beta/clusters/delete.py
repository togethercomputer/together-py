import json as json_lib

import click

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
def delete(ctx: click.Context, cluster_id: str, json: bool) -> None:
    """Delete a cluster by ID"""
    client: Together = ctx.obj

    if json:
        response = client.beta.clusters.delete(cluster_id=cluster_id)
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
        return

    cluster = client.beta.clusters.retrieve(cluster_id=cluster_id)
    ctx.obj.print_clusters([cluster])
    if not click.confirm(f"Clusters: Are you sure you want to delete cluster {cluster.cluster_name}?"):
        return

    click.echo("Clusters: Deleting cluster...")
    response = client.beta.clusters.delete(cluster_id=cluster_id)

    click.echo(f"Clusters: Deleted cluster {cluster.cluster_name}")
