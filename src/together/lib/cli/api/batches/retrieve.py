from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.batches._utils import print_batch_detail


async def retrieve(
    batch_id: Annotated[str, Parameter(help="The ID of the batch job")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Get details of a batch job."""
    response = await show_loading_status("Retrieving batch job...", config.client.batches.retrieve(batch_id))
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_batch_detail(response)
