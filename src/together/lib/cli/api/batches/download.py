from __future__ import annotations

import sys
import base64
from typing import Any, Optional, Annotated
from pathlib import Path

from cyclopts import Parameter, validators

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.files.retrieve_content import download_file_content

_TERMINAL_STATUSES = frozenset({"COMPLETED", "FAILED", "EXPIRED", "CANCELLED"})


def _is_directory_output(path: Path) -> bool:
    return path.is_dir() or path.suffix == ""


def _error_output_path(output: Path) -> Path:
    """Where to write the error file when *output* is a concrete file path."""
    suffix = output.suffix or ".jsonl"
    return output.with_name(f"{output.stem}.errors{suffix}")


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
        console.print(
            f"[red]Batch job is not ready to download yet[/red] "
            f"(status: {status or 'unknown'}). "
            f"Check progress with [primary]tg batches get {id}[/primary]."
        )
        sys.exit(1)

    if not job.output_file_id and not job.error_file_id:
        console.print(f"[red]Batch job has no output or error files to download[/red] (status: {status}).")
        sys.exit(1)

    if output is not None:
        saved: list[dict[str, str]] = []
        directory_output = _is_directory_output(output)
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
            err_dest = output if directory_output else _error_output_path(output)
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

    if not job.output_file_id:
        console.print(
            "[red]Batch job has no output file[/red]. "
            "Use [primary]--output[/primary] to download the error file instead."
        )
        sys.exit(1)

    raw = await download_file_content(
        config.client,
        job.output_file_id,
        stdout=True,
        loading_message="Downloading batch output...",
    )
    assert isinstance(raw, bytes)

    if config.json:
        try:
            payload: dict[str, Any] = {
                "batch_id": id,
                "output_file_id": job.output_file_id,
                "content": raw.decode("utf-8"),
            }
        except UnicodeDecodeError:
            payload = {
                "batch_id": id,
                "output_file_id": job.output_file_id,
                "content_base64": base64.b64encode(raw).decode("ascii"),
            }
        if job.error_file_id:
            payload["error_file_id"] = job.error_file_id
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    console.print(raw.decode("utf-8"))
    if job.error_file_id:
        console.print(f"\n[dim]Error file also available: tg batches download {id} --output ./out[/dim]")
