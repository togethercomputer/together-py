from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.components.model_dump import print_model_dump


async def model_limits(
    model: Annotated[str, Parameter(alias="-M", help="The model name to get fine-tuning limits for")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Get fine-tuning limits for a model."""
    response = await show_loading_status(
        "Fetching model limits...",
        config.client.fine_tuning.model_limits(model_name=model),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_model_dump(response, show_nulls=False)
