from __future__ import annotations

import re
from typing import Annotated, Any, Dict, List, Optional

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether, omit
from together.types import EndpointListHardwareResponse

from together.lib.utils.serializer import datetime_serializer
from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


def _format_hardware_options(
    hardware_options: EndpointListHardwareResponse, show_availability: bool = True
) -> None:
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
        if show_availability and hw.availability:
            status = hw.availability.status
            data["availability"] = (
                "✓ available" if status == "available" else ("✗ unavailable" if status == "unavailable" else "⚠ insufficient")
            )
        display_list.append(data)
    print(tabulate(display_list, headers="keys", numalign="left"))


@handle_endpoint_api_errors("Endpoints")
async def hardware(
    model: Optional[str] = None,
    json_output: bool = False,
    available: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List all available hardware options, optionally filtered by model."""
    hardware_options = await client.endpoints.list_hardware(model=model or omit)
    if available:
        hardware_options.data = [
            hw
            for hw in hardware_options.data
            if hw.availability is not None and hw.availability.status == "available"
        ]
    if json_output:
        import json as json_lib

        json_out = [hw.model_dump() for hw in hardware_options.data]
        print(json_lib.dumps(json_out, default=datetime_serializer, indent=2))
    else:
        _format_hardware_options(hardware_options, show_availability=model is not None)
