from __future__ import annotations

from typing import Literal

import click
from rich import print_json

from together import Together, omit
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@click.command()
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.option(
    "--type",
    type=click.Choice(["dedicated", "serverless"]),
    help="Filter by endpoint type",
)
@click.option(
    "--mine",
    is_flag=True,
    default=None,
    help="true (only mine), default=all",
)
@click.option(
    "--usage-type",
    type=click.Choice(["on-demand", "reserved"]),
    help="Filter by endpoint usage type",
)
@click.pass_context
@handle_api_errors("Endpoints")
@handle_endpoint_api_errors("Endpoints")
def list(
    ctx: click.Context,
    json: bool,
    type: Literal["dedicated", "serverless"] | None,
    usage_type: Literal["on-demand", "reserved"] | None,
    mine: bool | None,
) -> None:
    """List all inference endpoints (includes both dedicated and serverless endpoints)."""
    client: Together = ctx.obj

    endpoints = client.endpoints.list(
        type=type or omit,
        usage_type=usage_type or omit,
        mine=mine if mine is not None else omit,
    )

    if json:
        print_json(openapi_dumps(endpoints.data).decode("utf-8"))
        return

    if not endpoints:
        click.echo("No dedicated endpoints found", err=True)
        return

    click.echo("Endpoints:", err=True)
    # Only show autoscaling for user's own endpoints (when --mine is set)
    show_autoscaling = mine is True
    for endpoint in endpoints.data:
        ctx.obj.print_endpoint(
            endpoint,
            show_autoscaling=show_autoscaling,
        )
        click.echo()
