from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump


async def whoami(
    *,
    config: CLIConfigParameter,
) -> None:
    """Show identity information for the configured API key."""
    response = await show_loading_status("Loading identity...", config.client.whoami())

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_model_dump(response)
