from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.training._display import print_model_resource


async def extend_expiry(
    model_resources_id: Annotated[str, Parameter(help="ID of the model resource")],
    *,
    seconds: Annotated[
        int,
        Parameter(help="Seconds from now the resource must not stop for inactivity"),
    ],
    config: CLIConfigParameter,
) -> None:
    """Keep a ready model resource from stopping for inactivity.

    Moves the resource's expiry to at least this many seconds from now, and never earlier.
    Session operations already keep it up for its inactive timeout, so use this to stay up
    longer without operations. Fails if the resource is not ready.
    """
    resource = await show_loading_status(
        "Extending model resource expiry...",
        config.client.post_training.model_resources.extend_expiry(model_resources_id, seconds=seconds),
    )
    if config.json:
        console.print_json(openapi_dumps(resource).decode("utf-8"))
        return

    print_model_resource(resource)
