import json
import pathlib
from typing import get_args

import click

from together import Together
from together.types import FilePurpose
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument(
    "file",
    type=click.Path(exists=True, file_okay=True, resolve_path=True, readable=True, dir_okay=False),
    required=True,
)
@click.option(
    "--purpose",
    type=click.Choice(get_args(FilePurpose)),
    default="fine-tune",
    help="Purpose of file upload. Acceptable values in enum `together.types.FilePurpose`. Defaults to `fine-tunes`.",
)
@click.option(
    "--check/--no-check",
    default=True,
    help="Whether to check the file before uploading.",
)
@handle_api_errors("Files")
def upload(ctx: click.Context, file: pathlib.Path, purpose: FilePurpose, check: bool) -> None:
    """Upload file"""

    client: Together = ctx.obj

    response = client.files.upload(file=file, purpose=purpose, check=check)

    click.echo(json.dumps(response.model_dump(exclude_none=True), indent=4))
