from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def rm(
    id: Annotated[str, Parameter(help="Model ID to delete")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Delete a beta model."""
    await show_loading_status(
        "Deleting beta model...",
        config.client.beta.models.delete(id),
    )

    if config.json:
        console.print_json(openapi_dumps({"message": "Successfully deleted beta model"}).decode("utf-8"))
        return

    console.print("[green]√[/green] Beta model deleted.")
