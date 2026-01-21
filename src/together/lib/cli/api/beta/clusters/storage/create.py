import json as json_lib

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option(
    "--region",
    required=True,
    type=str,
    help="Region to create the storage volume in",
)
@click.option(
    "--size-tib",
    required=True,
    type=int,
    help="Size of the storage volume in TiB",
)
@click.option(
    "--volume-name",
    required=True,
    type=str,
    help="Name of the storage volume",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters Storage")
def create(ctx: click.Context, region: str, size_tib: int, volume_name: str, json: bool) -> None:
    """Create a storage volume"""
    client: Together = ctx.obj

    response = client.beta.clusters.storage.create(
        region=region,
        size_tib=size_tib,
        volume_name=volume_name,
    )

    if json:
        click.echo(json_lib.dumps(response.model_dump_json(), indent=2))
    else:
        click.echo(f"Storage volume created successfully")
        click.echo(response.volume_id)
