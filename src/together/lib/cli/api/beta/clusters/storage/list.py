import json as json_lib
from typing import Any, Dict, List

import click
from tabulate import tabulate

from together import Together
from together.lib.cli.api._utils import handle_api_errors
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


@click.command()
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
