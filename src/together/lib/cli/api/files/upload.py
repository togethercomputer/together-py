import pathlib
from typing import get_args

import click

from together import Together
from together.types import FilePurpose
from together._utils._json import openapi_dumps
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
@click.option(
    "--json",
    is_flag=True,
    help="Output the response in JSON format",
)
@handle_api_errors("Files")
def upload(ctx: click.Context, file: pathlib.Path, purpose: FilePurpose, check: bool, json: bool) -> None:
    """Upload file"""

    client: Together = ctx.obj

    response = client.files.upload(file=file, purpose=purpose, check=check)

    if json:
        click.echo(openapi_dumps(response.model_dump(exclude_none=True)))
        return

    click.echo(
        click.style("> Success! ", fg="blue")
        + f"File uploaded for {click.style(response.purpose, bold=True)}. File ID: {click.style(response.id, fg='green', bold=True)}"
    )
