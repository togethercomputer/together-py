from __future__ import annotations

import os
import sys
from typing import Optional, Annotated, cast, get_args
from pathlib import Path

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together.lib import check_file
from together.types import FilePurpose
from together._utils._json import openapi_dumps
from together.lib.resources.files import FileAlreadyExistsError
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def upload(
    file: Annotated[Path, Parameter(required=True, help="The file to upload")],
    purpose: Annotated[Optional[FilePurpose], Parameter(help="The purpose of the file")] = "fine-tune",
    no_check: Annotated[Optional[bool], Parameter(negative=(), help="Skip checking the file for issues")] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Upload file."""
    if config.json:
        os.environ.setdefault("TOGETHER_DISABLE_TQDM", "true")

    # Manually handle check here so we can exit and provide the user good error messages
    if not no_check:
        report = check_file(file)
        if report["is_check_passed"] is False:
            if config.json:
                console.print_json(openapi_dumps(report).decode("utf-8"))
            else:
                console.print(f"[red]❌ {escape_rich_markup(str(report['message']))}[/red]")

            # Make sure to exit
            sys.exit(1)

    try:
        purpose = cast(FilePurpose, purpose)
    except ValueError:
        console.print(f"[red]Invalid purpose '{purpose}'. Must be one of: {get_args(FilePurpose)}[/red]")
        sys.exit(1)

    try:
        response = await show_loading_status(
            "Uploading file",
            config.client.files.upload(
                file=file, purpose=purpose, check=False, raise_if_already_exists=not config.json
            ),
        )
    except FileAlreadyExistsError as e:
        console.print(
            f"[yellow]File already exists under ID: [bold]{e.file_id}[/bold]. "
            "If you want to re-upload it, please delete the existing file first.[/yellow]"
        )
        return

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return
    console.print(f"[green]Success![/green]")
    console.print(f"[blue]{response.id}[/blue]")
