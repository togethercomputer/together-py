from __future__ import annotations

import os
import sys
from typing import Optional, Annotated
from pathlib import Path

from cyclopts import Parameter, validators

from together import AsyncTogether
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def get_filename(client: AsyncTogether, id: str) -> str:
    r = await client.files.retrieve(id=id)
    return r.filename or id


async def retrieve_content(
    id: str,
    output: Annotated[
        Optional[Path],
        Parameter(
            help="The directory to save the content to", validator=validators.Path(file_okay=False, dir_okay=True)
        ),
    ] = None,
    stdout: Annotated[Optional[bool], Parameter(negative=(), help="Whether to output the content to stdout")] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Retrieve file content and output to file."""
    if stdout is False and output is None:
        console.print(f"[red]Invalid usage: Either --output <directory> or --stdout must be specified[/red]")
        sys.exit(1)

    response = await show_loading_status("Retrieving file contents...", config.client.files.content(id=id))

    if stdout:
        bytes = await response.read()
        console.print(bytes.decode("utf-8"))

    if output is not None:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        has_extension = Path(output).suffix != ""
        out_path = output if has_extension else f"{output}/{await get_filename(config.client, id)}"

        response = await config.client.files.content(id=id)
        await response.write_to_file(out_path)

        console.print(f"File saved to [blue]{out_path}[/blue]")
