from __future__ import annotations

import re
from typing import List, Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


async def hardware(
    model: Annotated[Optional[str], Parameter(help="Show only hardware compatible with the given model")] = None,
    available: Annotated[bool, Parameter(help="Show only available hardware for the given model")] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """List all available hardware options, optionally filtered by model."""
    hardware_options = await config.client.endpoints.list_hardware(model=model or omit)
    # hardware_options = model_data
    show_availability = model is not None and available
    if show_availability:
        hardware_options.data = [
            hw for hw in hardware_options.data if hw.availability is not None and hw.availability.status == "available"
        ]
    if config.json:
        console.print_json(openapi_dumps(hardware_options.data).decode("utf-8"))
        return

    table = ListTable("Hardware")
    table.add_primary_column("Hardware ID")
    table.add_column("GPU")
    table.add_column("Memory")
    table.add_column("Count")
    table.add_column("Price (per minute)")
    if show_availability:
        table.add_column("Availability")
    for hw in hardware_options.data:
        gpu = re.sub(r"\-\d+[a-zA-Z][a-zA-Z]$", "", hw.specs.gpu_type) if hw.specs and hw.specs.gpu_type else "N/A"
        memory = "N/A"
        count = "N/A"
        price = "N/A"
        if hw.specs:
            memory = f"{int(hw.specs.gpu_memory)}GB"
            count = str(hw.specs.gpu_count)
        if hw.pricing:
            price = f"${hw.pricing.cents_per_minute / 100:.2f}"
        fields: List[str] = []
        if show_availability and hw.availability:
            fields.append(
                (
                    "✓ available"
                    if hw.availability.status == "available"
                    else ("✗ unavailable" if hw.availability.status == "unavailable" else "⚠ insufficient")
                )
            )

        table.add_row(hw.id, gpu, memory, count, price, *fields)
    console.print(table)
