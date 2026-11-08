from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.api.models._utils import print_config_detail
from together.lib.cli.components.loader import show_loading_status


async def retrieve(
    id: Annotated[str, Parameter(help="Config revision ID (cr_...) to retrieve")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a model config revision."""
    response = await show_loading_status(
        "Loading model config...",
        config.client.models.configs.retrieve(id=id, project_id=config.project_id),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_config_detail(response)
