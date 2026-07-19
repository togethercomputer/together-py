from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._assert_explicit_project_id import assert_explicit_project_id
from together.lib.cli.api.beta.models.remote_uploads._utils import print_remote_upload_detail


async def create(
    model_id: Annotated[str, Parameter(help="Existing model or adapter ID to upload files to")],
    *,
    remote_url: Annotated[
        str,
        Parameter(name="--from", help="Hugging Face repository URL or presigned S3/GCS archive URL"),
    ],
    token: Annotated[
        Optional[str], Parameter(help="Source credential for a gated or private Hugging Face repository")
    ] = None,
    config: CLIConfigParameter,
) -> None:
    """Start a remote upload job."""

    await assert_explicit_project_id(config)

    response = await show_loading_status(
        "Starting remote upload...",
        config.client.beta.models.remote_uploads.create(
            model_id=model_id,
            remote_url=remote_url,
            token=token or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Remote upload job created.")
    print_remote_upload_detail(response)
