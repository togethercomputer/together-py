from __future__ import annotations

import sys
from typing import Annotated
from pathlib import Path

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.batches._utils import API_TO_ENDPOINT, BatchApiType, print_batch_detail


def _check_path_exists(path_string: str) -> bool:
    if path_string == "":
        return False
    p = Path(path_string)
    if p.is_dir():
        raise ValueError(f"Path {path_string} is a directory, not a file. Please provide a file path.")
    return p.exists() and p.is_file()


async def submit(
    file: Annotated[
        str,
        Parameter(help="File ID from Files API or local path to a file to upload"),
    ],
    api: Annotated[
        BatchApiType,
        Parameter(help="API to dispatch each line of the input file against"),
    ],
    *,
    config: CLIConfigParameter,
) -> None:
    """Submit a new batch job."""
    input_file_id = file
    if _check_path_exists(file):
        file_upload = await show_loading_status(
            "Uploading file...",
            config.client.files.upload(Path(file), purpose="batch-api", check=False),
        )
        input_file_id = file_upload.id

    response = await show_loading_status(
        "Submitting batch job...",
        config.client.batches.create(
            endpoint=API_TO_ENDPOINT[api],
            input_file_id=input_file_id,
        ),
    )

    job = response.job
    created = job is not None and bool(job.id)

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        if not created:
            sys.exit(1)
        return

    if not created:
        console.print("[red]x[/red] Batch job was not created")
        if response.warning:
            console.print(escape_rich_markup(response.warning))
        sys.exit(1)

    assert job is not None
    console.print(f"[green]√ Batch job submitted.[/green] [dim]({job.id})[/dim]")
    if response.warning:
        console.print(f"[yellow]{escape_rich_markup(response.warning)}[/yellow]")
    print_batch_detail(job)
    console.print("\n  You can track the job's progress with:")
    console.print(f"  [dim]-[/dim] [primary]tg batches get {job.id}[/primary]")
