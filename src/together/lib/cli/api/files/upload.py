from __future__ import annotations

from typing import Optional, Annotated, cast, get_args
from pathlib import Path

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together.lib import check_file
from together.types import FilePurpose
from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.resources.files import FileAlreadyExistsError
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.utils._json_mode import emit_json, is_json_mode, exit_with_message
from together.lib.cli.components.check_progress import CheckProgressTracker, should_show_check_progress
from together.lib.cli.components.upload_progress import upload_file_with_progress


async def upload(
    file: Annotated[Path, Parameter(required=True, help="The file to upload")],
    purpose: Annotated[Optional[FilePurpose], Parameter(help="The purpose of the file")] = "fine-tune",
    no_check: Annotated[Optional[bool], Parameter(negative=(), help="Skip checking the file for issues")] = False,
    *,
    config: CLIConfigParameter,
) -> None:
    """Upload file."""
    # Manually handle check here so we can exit and provide the user good error messages
    if not no_check:
        with CheckProgressTracker(file, enabled=should_show_check_progress(file, json_mode=config.json)) as tracker:
            report = check_file(
                file,
                purpose=purpose or "fine-tune",
                progress_callback=tracker.as_callback(),
            )
        if report["is_check_passed"] is False:
            if config.json:
                console.print_json(openapi_dumps(report).decode("utf-8"))
            else:
                console.print(f"[red]X {escape_rich_markup(str(report['message']))}[/red]")

            raise CliDiagnosticExit("File validation failed")

    try:
        purpose = cast(FilePurpose, purpose)
    except ValueError:
        allowed = ", ".join(str(item) for item in get_args(FilePurpose))
        exit_with_message(
            f"[red]Invalid purpose '{purpose}'. Must be one of: {get_args(FilePurpose)}[/red]",
            error=f"Invalid purpose '{purpose}'. Must be one of: {allowed}",
            diagnostic="Invalid file purpose",
        )

    try:
        response = await upload_file_with_progress(
            config.client.files.upload,
            file,
            enabled=not config.json,
            purpose=purpose,
            check=False,
            raise_if_already_exists=True,
        )
    except FileAlreadyExistsError as e:
        if is_json_mode():
            emit_json(
                {
                    "error": "File already exists. Delete the existing file before re-uploading.",
                    "file_id": e.file_id,
                }
            )
            raise SystemExit(1) from None
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
