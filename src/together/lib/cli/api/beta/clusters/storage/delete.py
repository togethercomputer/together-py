import json as json_lib

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument(
    "volume-id",
    required=True,
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters Storage")
def delete(ctx: click.Context, volume_id: str, json: bool) -> None:
    """Delete a storage volume"""
    client: Together = ctx.obj

    if json:
        response = client.beta.clusters.storage.delete(volume_id)
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
        return

    storage = client.beta.clusters.storage.retrieve(volume_id)
    ctx.obj.print_storage([storage])
    if not click.confirm(f"Clusters Storage: Are you sure you want to delete storage volume {storage.volume_name}?"):
        return

    click.echo("Clusters Storage: Deleting storage volume...")
    response = client.beta.clusters.storage.delete(volume_id)

    click.echo(f"Clusters Storage: Deleted storage volume {storage.volume_name}")
