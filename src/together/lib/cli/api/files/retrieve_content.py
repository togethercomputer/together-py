import os
from typing import Union
from pathlib import Path

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("id", type=str, required=True)
@click.option("--output", type=click.Path(file_okay=False, writable=True, dir_okay=True), help="Output filename")
@click.option("--stdout", is_flag=True, default=False, help="Output to stdout")
@handle_api_errors("Files")
def retrieve_content(ctx: click.Context, id: str, output: Union[str, None], stdout: bool) -> None:
    """Retrieve file content and output to file"""

    client: Together = ctx.obj

    if stdout is True:
        response = client.files.content(id=id)
        click.echo(response.read().decode("utf-8"))

    elif output is not None:
        os.makedirs(os.path.dirname(output), exist_ok=True)

        # If the user specified an output with an extension - that is a file name so write to that
        # If they only specified a directory, write to that directory with the file name from our api
        has_extension = Path(output).suffix != ""
        output = output if has_extension else f"{output}/{get_filename(client, id)}"

        with open(output, "wb") as f:
            response = client.files.content(id=id)
            f.write(response.read())
        click.echo(f"File saved to {output}")

    else:
        raise click.UsageError("Either --output <filename> or --stdout must be specified")


def get_filename(client: Together, id: str) -> str:
    return client.files.retrieve(id=id).filename
