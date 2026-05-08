from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def status(
    evaluation_id: Annotated[str, Parameter(help="The ID of the evaluation job")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Get the status and results of a specific evaluation job."""
    response = await show_loading_status("Retrieving eval status...", config.client.evals.status(evaluation_id))
    if config.json:
        console.print_json(openapi_dumps({"status": response.status}).decode("utf-8"))
        return

    console.print(f"Status: {response.status}")
