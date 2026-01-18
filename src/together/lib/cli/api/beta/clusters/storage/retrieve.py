import json as json_lib

import click
from rich import print

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
def retrieve(ctx: click.Context, volume_id: str, json: bool) -> None:
    """Retrieve a storage volume"""
    client: Together = ctx.obj

    if not json:
        click.echo(f"Clusters Storage: Retrieving storage volume...")

    response = client.beta.clusters.storage.retrieve(volume_id)

    if json:
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
    else:
        print(response)
