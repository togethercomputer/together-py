import json as json_lib
from typing import Any, Dict, List

import click
from tabulate import tabulate

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def list_regions(ctx: click.Context, json: bool) -> None:
    """List regions"""
    client: Together = ctx.obj

    response = client.beta.clusters.list_regions()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        data: List[Dict[str, Any]] = []
        for region in response.regions:
            data.append(
                {
                    "Name": region.name,
                    "Availability Zones": ", ".join(region.availability_zones) if region.availability_zones else "",
                    "Driver Versions": ", ".join(region.driver_versions) if region.driver_versions else "",
                }
            )
        click.echo(tabulate(data, headers="keys", tablefmt="grid"))
