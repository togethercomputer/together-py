from __future__ import annotations

import sys
from typing import NoReturn, Optional, Annotated
from pathlib import Path

from cyclopts import Parameter, validators

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console, error_console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.files.retrieve_content import (
    is_directory_output,
    download_file_content,
    stream_file_content_to_stdout,
)

_TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "EXPIRED", "CANCELLED"})


def _error_output_path(output: Path) -> Path:
    """Where to write the error file when *output* is a concrete file path."""
    suffix = output.suffix or ".jsonl"
    return output.with_name(f"{output.stem}.errors{suffix}")


def _fail(*, json_mode: bool, error: str, rich_message: str) -> NoReturn:
    if json_mode:
        console.print_json(openapi_dumps({"error": error}).decode("utf-8"))
    else:
        console.print(rich_message)
    sys.exit(1)


async def download(
    id: Annotated[str, Parameter(help="The ID of the batch job")],
    output: Annotated[
        Optional[Path],
        Parameter(
            name=["--output", "-o"],
            help="File or directory to save batch result files to; omit to print output to stdout",
            validator=validators.Path(file_okay=True, dir_okay=True),
        ),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Download output (and error) files for a batch job."""
    job = await show_loading_status("Retrieving batch job...", config.client.batches.retrieve(id))
    status = job.status or ""

    if status not in _TERMINAL_STATUSES:
        _fail(
            json_mode=config.json,
            error=(
                f"Batch job is not ready to download yet (status: {status or 'unknown'}). "
                f"Check progress with tg batches get {id}."
            ),
            rich_message=(
                f"[red]Batch job is not ready to download yet[/red] "
                f"(status: {status or 'unknown'}). "
                f"Check progress with [primary]tg batches get {id}[/primary]."
            ),
        )

    if not job.output_file_id and not job.error_file_id:
        _fail(
            json_mode=config.json,
            error=f"Batch job has no output or error files to download (status: {status}).",
            rich_message=f"[red]Batch job has no output or error files to download[/red] (status: {status}).",
        )

    if output is not None:
        saved: list[dict[str, str]] = []
        directory_output = is_directory_output(output)
        error_file_id = job.error_file_id

        if job.output_file_id:
            out_path = await download_file_content(
                config.client,
                job.output_file_id,
                output=output,
                loading_message="Downloading batch output...",
            )
            assert isinstance(out_path, Path)
            saved.append({"kind": "output", "id": job.output_file_id, "path": str(out_path)})
        elif error_file_id and not directory_output:
            # No output file — write the error file to the exact path the user asked for.
            err_path = await download_file_content(
                config.client,
                error_file_id,
                output=output,
                loading_message="Downloading batch errors...",
            )
            assert isinstance(err_path, Path)
            saved.append({"kind": "error", "id": error_file_id, "path": str(err_path)})
            error_file_id = None

        if error_file_id:
            if directory_output and saved:
                # Server filenames are not unique across output/error files.
                err_dest = _error_output_path(Path(saved[0]["path"]))
            elif directory_output:
                err_dest = output
            else:
                err_dest = _error_output_path(output)
            err_path = await download_file_content(
                config.client,
                error_file_id,
                output=err_dest,
                loading_message="Downloading batch errors...",
            )
            assert isinstance(err_path, Path)
            saved.append({"kind": "error", "id": error_file_id, "path": str(err_path)})

        if config.json:
            console.print_json(openapi_dumps({"batch_id": id, "files": saved}).decode("utf-8"))
            return

        for item in saved:
            label = "Output" if item["kind"] == "output" else "Errors"
            console.print(f"[green]√[/green] {label} saved to [blue]{item['path']}[/blue]")
        return

    output_file_id = job.output_file_id
    if not output_file_id:
        _fail(
            json_mode=config.json,
            error="Batch job has no output file. Use --output to download the error file instead.",
            rich_message=(
                "[red]Batch job has no output file[/red]. "
                "Use [primary]--output[/primary] to download the error file instead."
            ),
        )

    if config.json:
        _fail(
            json_mode=True,
            error="Pass --output to download batch result files; --json does not print file contents to stdout.",
            rich_message="",
        )

    await stream_file_content_to_stdout(config.client, output_file_id)
    if job.error_file_id:
        error_console.print(
            f"[dim]Error file also available: tg batches download {id} --output ./out[/dim]",
        )
