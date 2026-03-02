from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


async def list_events(
    fine_tune_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """List fine-tuning events."""
    response = await config.client.fine_tuning.list_events(fine_tune_id)
    response.data = response.data or []

    if config.json:
        console.print_json(openapi_dumps(response.data).decode("utf-8"))
        return

    table = ListTable()
    table.add_primary_column("Type")
    table.add_column("Message")
    table.add_column("Created At")

    for i in response.data:
        table.add_row(i.type, i.message, format_timestamp(i.created_at))

    console.print(table)
