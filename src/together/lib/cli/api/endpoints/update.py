from __future__ import annotations

import sys
from typing import Any, Dict

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.argument("endpoint-id", required=True)
@click.option(
    "--display-name",
    help="A new human-readable name for the endpoint",
)
@click.option(
    "--min-replicas",
    type=int,
    help="New minimum number of replicas to maintain",
)
@click.option(
    "--max-replicas",
    type=int,
    help="New maximum number of replicas to scale up to",
)
@click.option(
    "--inactive-timeout",
    type=int,
    help="Number of minutes of inactivity after which the endpoint will be automatically stopped. Set to 0 to disable.",
)
@click.pass_obj
@handle_api_errors("Endpoints")
def update(
    client: Together,
    endpoint_id: str,
    display_name: str | None,
    min_replicas: int | None,
    max_replicas: int | None,
    inactive_timeout: int | None,
) -> None:
    """Update a dedicated inference endpoint's configuration."""
    if not any([display_name, min_replicas, max_replicas, inactive_timeout]):
        click.echo("Error: At least one update option must be specified", err=True)
        sys.exit(1)

    # Build kwargs for the update
    kwargs: Dict[str, Any] = {}
    if display_name is not None:
        kwargs["display_name"] = display_name

    if min_replicas is not None or max_replicas is not None:
        kwargs["autoscaling"] = {}
        if min_replicas is not None:
            kwargs["autoscaling"]["min_replicas"] = min_replicas
        if max_replicas is not None:
            kwargs["autoscaling"]["max_replicas"] = max_replicas

    if inactive_timeout is not None:
        kwargs["inactive_timeout"] = inactive_timeout

    client.endpoints.update(endpoint_id, **kwargs)

    # Print what was updated
    click.echo("Updated endpoint configuration:", err=True)
    if display_name:
        click.echo(f"  Display name: {display_name}", err=True)
    if min_replicas:
        click.echo(f"  Min replicas: {min_replicas}", err=True)
    if max_replicas:
        click.echo(f"  Max replicas: {max_replicas}", err=True)
    if inactive_timeout is not None:
        click.echo(f"  Inactive timeout: {inactive_timeout} minutes", err=True)

    click.echo("Successfully updated endpoint", err=True)
    click.echo(endpoint_id)
