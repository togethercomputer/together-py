from __future__ import annotations

import click

from together.types import DedicatedEndpoint
from together.types.endpoint_list_response import Data as DedicatedEndpointListItem

from .list import list
from .stop import stop
from .start import start
from .create import create
from .delete import delete
from .update import update
from .hardware import hardware
from .retrieve import retrieve
from .availability_zones import availability_zones


@click.group()
@click.pass_context
def endpoints(ctx: click.Context) -> None:
    """Endpoints API commands"""

    def print_endpoint(endpoint: DedicatedEndpoint | DedicatedEndpointListItem) -> None:
        """Print endpoint details in a Docker-like format or JSON."""

        # Print header info
        click.echo(f"ID:\t\t{endpoint.id}")
        click.echo(f"Name:\t\t{endpoint.name}")

        if isinstance(endpoint, DedicatedEndpoint):
            click.echo(f"Display Name:\t{endpoint.display_name}")
            click.echo(f"Hardware:\t{endpoint.hardware}")
            click.echo(
                f"Autoscaling:\tMin={endpoint.autoscaling.min_replicas}, Max={endpoint.autoscaling.max_replicas}"
            )

        click.echo(f"Model:\t\t{endpoint.model}")
        click.echo(f"Type:\t\t{endpoint.type}")
        click.echo(f"Owner:\t\t{endpoint.owner}")
        click.echo(f"State:\t\t{endpoint.state}")
        click.echo(f"Created:\t{endpoint.created_at}")

    ctx.obj.print_endpoint = print_endpoint
    pass


endpoints.add_command(hardware)
endpoints.add_command(create)
endpoints.add_command(retrieve)
endpoints.add_command(stop)
endpoints.add_command(start)
endpoints.add_command(delete)
endpoints.add_command(list)
endpoints.add_command(update)
endpoints.add_command(availability_zones)
