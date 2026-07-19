from __future__ import annotations

from typing_extensions import Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.models.remote_uploads._utils import print_remote_upload_detail


async def retrieve(
    id: Annotated[str, Parameter(help="Remote upload job ID")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve a remote upload job."""

    response = await show_loading_status(
        "Loading remote upload job...", config.client.beta.models.remote_uploads.retrieve(id)
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    print_remote_upload_detail(response)
