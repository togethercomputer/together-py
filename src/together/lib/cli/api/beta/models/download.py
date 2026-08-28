from __future__ import annotations

import os
import sys
import shutil
import asyncio
import tempfile
from typing import Any, Literal, Optional, cast
from pathlib import Path
from dataclasses import dataclass
from typing_extensions import Annotated

import httpx
from cyclopts import Parameter

from together import omit
from together._utils import path_template
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.api.beta.models.upload import (
    PART_SIZE_BYTES,
    FILE_CONCURRENCY,
    PART_CONCURRENCY,
    _file_etag,
)
from together.lib.cli.components.upload_progress import format_bytes
from together.lib.cli.components.download_progress import DownloadProgressTracker

PART_DOWNLOAD_TIMEOUT_SECONDS = 30 * 60
PART_DOWNLOAD_MAX_ATTEMPTS = 5


@dataclass(frozen=True)
class RemotePart:
    number: int
    size: int
    url: str
    headers: dict[str, str]
    offset: int


@dataclass(frozen=True)
class RemoteFile:
    path: str
    hash: str
    size: int
    parts: list[RemotePart]


def _parse_object_and_revision(model_id: str, revision: str | None) -> tuple[str, str | None]:
    if "@" in model_id:
        object_id, embedded = model_id.rsplit("@", 1)
        if not object_id:
            raise ValueError(f"invalid model id: {model_id!r}")
        if revision and embedded and revision != embedded:
            raise ValueError("conflicting revisions from model id (@…) and --revision")
        return object_id, revision or embedded or None
    return model_id, revision


def _normalize_files(files: list[str] | None) -> list[str]:
    if not files:
        return []
    out: list[str] = []
    for entry in files:
        for part in entry.split(","):
            path = part.strip()
            if path:
                out.append(path)
    return out


def _as_int(value: Any) -> int:
    if value is None:
        return 0
    return int(value)


def _huggingface_snapshot_path(base_path: Path, object_id: str, revision_id: str) -> Path:
    if "/" not in object_id:
        raise ValueError(f'HuggingFace layout requires project/name, got "{object_id}"')
    project, name = object_id.split("/", 1)
    if not project or not name:
        raise ValueError(f'HuggingFace layout requires project/name, got "{object_id}"')

    repo = f"models--{project}--{name}"
    refs_dir = base_path / repo / "refs"
    refs_dir.mkdir(parents=True, exist_ok=True)
    (refs_dir / "main").write_text(revision_id, encoding="utf-8")
    return base_path / repo / "snapshots" / revision_id


def _parse_remote_files(payload: list[dict[str, Any]]) -> list[RemoteFile]:
    files: list[RemoteFile] = []
    for remote in payload:
        path = str(remote.get("path") or "")
        if not path:
            raise ValueError("download response missing file path")
        raw_parts = list(cast(list[dict[str, Any]], remote.get("parts") or []))
        parts: list[RemotePart] = []
        offset = 0
        for raw_part in raw_parts:
            size = _as_int(raw_part.get("sizeBytes"))
            parts.append(
                RemotePart(
                    number=_as_int(raw_part.get("partNumber")),
                    size=size,
                    url=str(raw_part.get("url") or ""),
                    headers=dict(cast(dict[str, str], raw_part.get("headers") or {})),
                    offset=offset,
                )
            )
            offset += size
        files.append(
            RemoteFile(
                path=path,
                hash=str(remote.get("hash") or ""),
                size=_as_int(remote.get("sizeBytes")),
                parts=parts,
            )
        )
    return files


def _check_disk_space(base_path: Path, need_bytes: int) -> None:
    base_path.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(base_path)
    if usage.free < need_bytes:
        raise ValueError(f"insufficient disk space: need {format_bytes(need_bytes)}, have {format_bytes(usage.free)}")


def _preallocate_file(path: Path, size: int) -> None:
    with path.open("wb") as file:
        file.truncate(size)


def _write_at(path: Path, offset: int, data: bytes) -> None:
    with path.open("r+b") as file:
        file.seek(offset)
        file.write(data)


async def _download_part(
    http_client: httpx.AsyncClient,
    part: RemotePart,
    tmp_path: Path,
    progress: DownloadProgressTracker | None = None,
) -> None:
    last_error: Exception | None = None
    for attempt in range(PART_DOWNLOAD_MAX_ATTEMPTS):
        try:
            response = await http_client.get(part.url, headers=part.headers)
            if response.status_code in {httpx.codes.OK, httpx.codes.PARTIAL_CONTENT}:
                data = response.content
                if len(data) != part.size:
                    raise ValueError(f"part {part.number}: expected {part.size} bytes, got {len(data)}")
                await asyncio.to_thread(_write_at, tmp_path, part.offset, data)
                if progress is not None:
                    await progress.bytes_completed(part.size)
                return
            response_text = response.text
            if 400 <= response.status_code < 500 and response.status_code != httpx.codes.TOO_MANY_REQUESTS:
                raise ValueError(f"download status {response.status_code}: {response_text}")
            last_error = ValueError(f"download status {response.status_code}: {response_text}")
        except (httpx.HTTPError, ValueError, OSError) as exc:
            last_error = exc
            if isinstance(exc, ValueError) and str(exc).startswith("download status 4"):
                raise

        if attempt < PART_DOWNLOAD_MAX_ATTEMPTS - 1:
            await asyncio.sleep(2**attempt)

    assert last_error is not None
    raise ValueError(f"download after retries: {last_error}") from last_error


async def _should_skip(file: RemoteFile, dest: Path) -> bool:
    if not dest.is_file():
        return False
    try:
        if dest.stat().st_size != file.size:
            return False
        etag = await asyncio.to_thread(_file_etag, dest, PART_SIZE_BYTES)
    except OSError:
        return False
    return etag == file.hash


async def _download_file(
    http_client: httpx.AsyncClient,
    part_semaphore: asyncio.Semaphore,
    file: RemoteFile,
    base_path: Path,
    progress: DownloadProgressTracker | None = None,
) -> None:
    dest = base_path / file.path
    if await _should_skip(file, dest):
        if progress is not None:
            await progress.bytes_completed(file.size)
            await progress.file_completed(file.path, skipped=True)
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = await asyncio.to_thread(tempfile.mkstemp, prefix=".transfer-dl-", dir=dest.parent)
    tmp_path = Path(tmp_name)
    try:
        os.close(tmp_fd)
        await asyncio.to_thread(_preallocate_file, tmp_path, file.size)

        async def download_one(part: RemotePart) -> None:
            async with part_semaphore:
                await _download_part(http_client, part, tmp_path, progress=progress)

        await asyncio.gather(*(download_one(part) for part in file.parts))
        await asyncio.to_thread(os.replace, tmp_path, dest)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    if progress is not None:
        await progress.file_completed(file.path)


async def _download_files(
    files: list[RemoteFile],
    base_path: Path,
    *,
    progress: DownloadProgressTracker | None = None,
) -> None:
    file_semaphore = asyncio.Semaphore(FILE_CONCURRENCY)
    part_semaphore = asyncio.Semaphore(PART_CONCURRENCY)
    timeout = httpx.Timeout(PART_DOWNLOAD_TIMEOUT_SECONDS)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as http_client:

        async def download_one(file: RemoteFile) -> None:
            async with file_semaphore:
                await _download_file(
                    http_client,
                    part_semaphore,
                    file,
                    base_path,
                    progress=progress,
                )

        await asyncio.gather(*(download_one(file) for file in files))


async def _download_model_files(
    *,
    config: CLIConfig,
    object_id: str,
    local_path: Path,
    revision_id: str | None,
    paths: list[str],
    hf_format: bool,
    show_progress: bool = False,
) -> dict[str, Any]:
    rev = revision_id
    if not rev:
        list_response = await config.client.beta.models.list_files(object_id, revision_id=omit)
        rev = list_response.revision_id
        if not rev:
            raise ValueError("could not resolve latest revision")

    body: dict[str, Any] = {
        "objectId": object_id,
        "paths": paths,
        "revisionId": rev,
    }
    download_response = cast(
        dict[str, Any],
        await config.client.post(
            path_template(
                "/projects/{project_id}/models/download",
                project_id=config.project_id,
            ),
            cast_to=object,
            body=body,
        ),
    )
    remote_files = _parse_remote_files(list(cast(list[dict[str, Any]], download_response.get("files") or [])))
    rev = str(download_response.get("revisionId") or rev)

    dst = local_path
    if hf_format:
        dst = _huggingface_snapshot_path(local_path, object_id, rev)

    total_bytes = sum(file.size for file in remote_files)
    _check_disk_space(dst, total_bytes)

    progress = DownloadProgressTracker(
        total_bytes=total_bytes,
        total_files=len(remote_files),
        enabled=show_progress and len(remote_files) > 0,
    )
    if show_progress and remote_files:
        console.print(f"Downloading {len(remote_files)} file(s), {format_bytes(total_bytes)} total")
        console.print(f"[dim]Revision:[/dim] {rev}")
    with progress:
        await _download_files(remote_files, dst, progress=progress)

    return {
        "revisionId": rev,
        "path": str(dst),
        "files": len(remote_files),
        "bytes": total_bytes,
        "skipped": progress.skipped_files,
    }


async def download(
    model_id: Annotated[str, Parameter(help="Model or adapter ID (ml_...) or project-qualified name")],
    local_path: Annotated[Path, Parameter(help="Local directory to write files into")],
    *,
    revision: Annotated[
        Optional[str], Parameter(help="Revision ID to download; defaults to the latest revision")
    ] = None,
    files: Annotated[
        Optional[list[str]],
        Parameter(
            help="Restrict to specific file paths (repeatable; commas allowed)",
            negative_iterable=(),
        ),
    ] = None,
    format: Annotated[
        Optional[Literal["hf"]],
        Parameter(name="format", help="Output layout; use hf for a Hugging Face snapshot"),
    ] = None,
    config: CLIConfigParameter,
) -> None:
    """Download files from a beta model or adapter."""

    try:
        object_id, resolved_revision = _parse_object_and_revision(model_id, revision)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    # Ensure we use the v2 apis for this
    config.client.base_url = "https://api.together.ai/v2"

    if config.json:
        try:
            result = await _download_model_files(
                config=config,
                object_id=object_id,
                local_path=Path(local_path),
                revision_id=resolved_revision,
                paths=_normalize_files(files),
                hf_format=format == "hf",
            )
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            sys.exit(1)
        console.print_json(data=result)
        return

    console.print(f"Downloading {object_id} to {local_path}...")
    try:
        await _download_model_files(
            config=config,
            object_id=object_id,
            local_path=Path(local_path),
            revision_id=resolved_revision,
            paths=_normalize_files(files),
            hf_format=format == "hf",
            show_progress=True,
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)
    console.print("Download complete")
