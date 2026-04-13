import json as json_lib
from typing import Any, Dict, List

import click
from rich import print
from tabulate import tabulate

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
def list_regions(ctx: click.Context, json: bool) -> None:
    """List regions"""
    client: Together = ctx.obj

    response = client.beta.clusters.list_regions()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        data: List[Dict[str, Any]] = []
        for region in response.regions:
            driver_versions: list[str] = []
            for driver_version in region.driver_versions:
                driver_versions.append(
                    f"[dim]NVIDIA Driver:[/dim] [blue]{driver_version.nvidia_driver_version}[/blue] [dim]CUDA Version:[/dim] [blue]{driver_version.cuda_version}[/blue]"
                )

            data.append(
                {
                    "Name": region.name,
                    "Supported GPU Types": ", ".join(region.supported_instance_types)
                    if region.supported_instance_types
                    else "",
                    "Driver Versions": "\n".join(driver_versions) if driver_versions else "",
                }
            )
        print(tabulate(data, headers="keys", tablefmt="grid"))
