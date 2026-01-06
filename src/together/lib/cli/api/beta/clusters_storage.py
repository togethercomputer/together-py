import json as json_lib
from typing import Any, Dict, List

import click
from rich import print
from tabulate import tabulate

from together import Together
from together.lib.cli.api.utils import handle_api_errors
from together.types.beta.clusters import ClusterStorage


def print_storage(storage: List[ClusterStorage]) -> None:
    data: List[Dict[str, Any]] = []
    for volume in storage:
        data.append(
            {
                "ID": volume.volume_id,
                "Name": volume.volume_name,
                "Size": volume.size_tib,
            }
        )
    click.echo(tabulate(data, headers="keys", tablefmt="grid"))


@click.group()
@click.pass_context
def storage(ctx: click.Context) -> None:
    """Clusters Storage API commands"""
    pass


@storage.command()
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


@storage.command()
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


@storage.command()
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
    print_storage([storage])
    if not click.confirm(f"Clusters Storage: Are you sure you want to delete storage volume {storage.volume_name}?"):
        return

    click.echo("Clusters Storage: Deleting storage volume...")
    response = client.beta.clusters.storage.delete(volume_id)

    click.echo(f"Clusters Storage: Deleted storage volume {storage.volume_name}")


@storage.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters Storage")
def list(ctx: click.Context, json: bool) -> None:
    """List storage volumes"""
    client: Together = ctx.obj

    response = client.beta.clusters.storage.list()

    if json:
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
    else:
        print_storage(response.volumes)
