from __future__ import annotations

import re
import json as json_lib
from typing import Any, Dict, List

import click
from tabulate import tabulate

from together import Together, omit
from together.types import HardwareListResponse
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
    hardware_options = client.hardware.list(model=model or omit)

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
        _format_hardware_options(hardware_options, show_availability=model is not None)


def _format_hardware_options(hardware_options: HardwareListResponse, show_availability: bool = True) -> None:
    display_list: List[Dict[str, Any]] = []

    for hw in hardware_options.data:
        data = {
            "Hardware ID": hw.id,
            "GPU": re.sub(r"\-\d+[a-zA-Z][a-zA-Z]$", "", hw.specs.gpu_type)
            if hw.specs and hw.specs.gpu_type
            else "N/A",
            "Memory": f"{int(hw.specs.gpu_memory)}GB" if hw.specs else "N/A",
            "Count": hw.specs.gpu_count if hw.specs else "N/A",
            "Price (per minute)": (f"${hw.pricing.cents_per_minute / 100:.2f}" if hw.pricing else "N/A"),
        }

        if show_availability:
            status_display = "—"
            if hw.availability:
                status = hw.availability.status
                # Add visual indicators for status
                if status == "available":
                    status_display = click.style("✓ available", fg="green")
                elif status == "unavailable":
                    status_display = click.style("✗ unavailable", fg="red")
                else:  # insufficient
                    status_display = click.style("⚠ insufficient", fg="yellow")
                data["availability"] = status_display
        display_list.append(data)

    click.echo(tabulate(display_list, headers="keys", numalign="left"))
