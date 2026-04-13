import os
import sys
import json as json_lib
import pathlib
from typing import get_args

import click
from rich import print, print_json

from together import Together
from together.lib import check_file
from together.types import FilePurpose
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
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
@auto_track_command
def upload(ctx: click.Context, file: pathlib.Path, purpose: FilePurpose, check: bool, json: bool) -> None:
    """Upload file"""

    client: Together = ctx.obj
    if json:
        os.environ.setdefault("TOGETHER_DISABLE_TQDM", "true")

    # Manually handle check here so we can exit and provide the user good error messages
    if check:
        report = check_file(file)
        if report["is_check_passed"] is False:
            if json:
                print_json(json_lib.dumps(report))
            else:
                print(f"❌ {report['message']}")

            # Make sure to exit
            sys.exit(1)

    response = client.files.upload(file=file, purpose=purpose, check=False)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    click.echo(
        click.style("> Success! ", fg="blue")
        + f"File uploaded for {click.style(response.purpose, bold=True)}. File ID: {click.style(response.id, fg='green', bold=True)}"
    )
