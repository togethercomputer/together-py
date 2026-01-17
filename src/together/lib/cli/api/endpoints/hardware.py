from __future__ import annotations

import json as json_lib

import click

from together import Together, omit
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer


@click.command()
@click.option("--model", help="Filter hardware options by model")
@click.option("--json", is_flag=True, help="Print output in JSON format")
@click.option(
    "--available",
    is_flag=True,
    help="Print only available hardware options (can only be used if model is passed in)",
)
@click.pass_obj
@handle_api_errors("Endpoints")
def hardware(client: Together, model: str | None, json: bool, available: bool) -> None:
    """List all available hardware options, optionally filtered by model."""
    message = "Available hardware options:" if available else "All hardware options:"
    click.echo(message, err=True)
    hardware_options = client.hardware.list(model=model or omit)
    # hardware_options = client.endpoints.list_hardware(model)
    if available:
        hardware_options.data = [
            hardware
            for hardware in hardware_options.data
            if hardware.availability is not None and hardware.availability.status == "available"
        ]

    if json:
        json_output = [hardware.model_dump() for hardware in hardware_options.data]
        click.echo(json_lib.dumps(json_output, default=datetime_serializer, indent=2))
    else:
        for hardware in hardware_options.data:
            click.echo(f"  {hardware.id}", err=True)
