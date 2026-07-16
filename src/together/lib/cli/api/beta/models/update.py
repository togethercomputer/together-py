from __future__ import annotations

import sys
from typing import Any, List, Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models._utils import print_model_detail


async def update(
    id: Annotated[str, Parameter(help="Model ID to update")],
    name: Annotated[Optional[str], Parameter(help="Updated inference-addressable name")] = None,
    description: Annotated[Optional[str], Parameter(help="Updated description")] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Update a beta model."""

    update_mask: List[str] = []
    body: dict[str, Any] = {}

    if name is not None:
        body["name"] = name
        update_mask.append("name")
    if description is not None:
        body["description"] = description
        update_mask.append("description")

    if not update_mask:
        console.print("Error: At least one update option must be specified.")
        sys.exit(1)

    response = await show_loading_status(
        "Updating beta model...",
        config.client.beta.models.update(
            id,
            **body,
            update_mask=",".join(update_mask),
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Beta model updated.\n")
    await print_model_detail(response, config=config)
