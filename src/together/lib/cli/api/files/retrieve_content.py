from __future__ import annotations

import sys
import base64
from typing import Optional, Annotated
from pathlib import Path

from cyclopts import Parameter, validators

from together import AsyncTogether
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


def safe_download_filename(filename: str, *, fallback: str) -> str:
    """Return a single path segment from a server-controlled filename.

    Strips directory components so values like ``../../etc/passwd`` cannot escape
    the user-specified ``--output`` directory.
    """
    name = Path(str(filename).replace("\\", "/")).name
    if not name or name in {".", ".."}:
        name = Path(str(fallback).replace("\\", "/")).name
    if not name or name in {".", ".."}:
        return "download"
    return name


def resolve_download_path(output_dir: Path, filename: str) -> Path:
    """Join *filename* under *output_dir*, rejecting paths that escape it."""
    out_path = (output_dir / filename).resolve()
    output_resolved = output_dir.resolve()
    if not out_path.is_relative_to(output_resolved):
        return output_resolved / "download"
    return out_path


async def get_filename(client: AsyncTogether, id: str) -> str:
    r = await client.files.retrieve(id=id)
    return safe_download_filename(r.filename or "", fallback=id)


def is_directory_output(path: Path) -> bool:
    """True when *path* should be treated as a destination directory.

    Existing files (including suffix-less names like ``./results``) are files.
    Missing suffix-less paths are directories to create.
    """
    if path.is_dir():
        return True
    if path.exists():
        return False
    return path.suffix == ""


async def stream_file_content_to_stdout(client: AsyncTogether, id: str) -> None:
    """Stream file bytes to stdout without buffering the whole body."""
    async with client.files.with_streaming_response.content(id=id) as response:
        async for chunk in response.iter_bytes():
            sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()


async def download_file_content(
    client: AsyncTogether,
    id: str,
    *,
    output: Path | None = None,
    stdout: bool = False,
    loading_message: str = "Retrieving file contents...",
) -> Path | bytes:
    """Download file content to *output*, or return raw bytes when *stdout* is True."""
    if stdout is False and output is None:
        raise ValueError("Either output or stdout must be specified")
    if stdout is True and output is not None:
        raise ValueError("--stdout and --output cannot be used together")

    async with client.files.with_streaming_response.content(id=id) as response:
        if stdout:
            return await response.read()

        assert output is not None
        if is_directory_output(output):
            output.mkdir(parents=True, exist_ok=True)
            out_path = resolve_download_path(output, await get_filename(client, id))
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            out_path = output

        await show_loading_status(loading_message, response.stream_to_file(out_path))
        return out_path


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

    if stdout is True and output is not None:
        console.print(f"[red]Invalid usage: --stdout and --output cannot be used together[/red]")
        sys.exit(1)

    result = await download_file_content(config.client, id, output=output, stdout=bool(stdout))

    if isinstance(result, bytes):
        if config.json:
            try:
                payload = {"id": id, "content": result.decode("utf-8")}
            except UnicodeDecodeError:
                payload = {"id": id, "content_base64": base64.b64encode(result).decode("ascii")}
            console.print_json(openapi_dumps(payload).decode("utf-8"))
        else:
            console.print(result.decode("utf-8"))
        return

    if config.json:
        console.print_json(openapi_dumps({"id": id, "path": str(result)}).decode("utf-8"))
    else:
        console.print(f"File saved to [blue]{result}[/blue]")
