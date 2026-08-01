from __future__ import annotations

import sys
import math
import asyncio
import hashlib
from typing import Any, Annotated, AsyncIterator, cast
from pathlib import Path
from dataclasses import dataclass

import httpx
from cyclopts import Parameter
from rich.progress import (
    TaskID,
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    DownloadColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from together._utils import path_template
from together.lib.cli.utils.config import CLIConfig, CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.utils._assert_explicit_project_id import assert_explicit_project_id

PART_SIZE_BYTES = 20 * 1024 * 1024
FILE_CONCURRENCY = 16
PART_CONCURRENCY = 256
PART_UPLOAD_TIMEOUT_SECONDS = 30 * 60
PART_UPLOAD_MAX_ATTEMPTS = 5


@dataclass(frozen=True)
class LocalPart:
    number: int
    offset: int
    size: int


@dataclass
class LocalFile:
    abs_path: Path
    path: str
    size: int
    hash: str
    parts: list[LocalPart]


def _calculate_parts(file_size: int, part_size: int = PART_SIZE_BYTES) -> list[LocalPart]:
    if file_size <= 0:
        return []
    parts: list[LocalPart] = []
    for index in range(math.ceil(file_size / part_size)):
        offset = index * part_size
        parts.append(LocalPart(number=index + 1, offset=offset, size=min(part_size, file_size - offset)))
    return parts


def _etag_from_md5s(md5s: list[bytes]) -> str:
    if len(md5s) == 1:
        return md5s[0].hex()
    return f"{hashlib.md5(b''.join(md5s)).hexdigest()}-{len(md5s)}"  # noqa: S324


def _file_etag(path: Path, chunk_size: int = PART_SIZE_BYTES) -> str:
    md5s: list[bytes] = []
    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            md5s.append(hashlib.md5(chunk).digest())  # noqa: S324
    return _etag_from_md5s(md5s)


def _collect_file_paths(local_path: Path) -> list[tuple[Path, str, int]]:
    info = local_path.stat()
    if not info.st_mode:
        return []
    if local_path.is_file():
        if info.st_size == 0:
            return []
        return [(local_path, local_path.name, info.st_size)]

    files: list[tuple[Path, str, int]] = []
    for path in sorted(local_path.rglob("*")):
        relative = path.relative_to(local_path)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if not path.is_file():
            continue
        size = path.stat().st_size
        if size == 0:
            continue
        files.append((path, relative.as_posix(), size))
    return files


async def _prepare_file(abs_path: Path, relative_path: str, size: int) -> LocalFile:
    return LocalFile(
        abs_path=abs_path,
        path=relative_path,
        size=size,
        hash=await asyncio.to_thread(_file_etag, abs_path),
        parts=_calculate_parts(size),
    )


async def _prepare_files(local_path: Path) -> list[LocalFile]:
    try:
        paths = _collect_file_paths(local_path)
    except OSError as exc:
        raise ValueError(f'stat "{local_path}": {exc}') from exc

    semaphore = asyncio.Semaphore(FILE_CONCURRENCY)

    async def prepare(path: Path, relative_path: str, size: int) -> LocalFile:
        async with semaphore:
            return await _prepare_file(path, relative_path, size)

    return await asyncio.gather(*(prepare(path, relative_path, size) for path, relative_path, size in paths))


def _create_upload_body(
    *,
    object_id: str,
    files: list[LocalFile],
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "objectId": object_id,
        "files": [
            {
                "path": file.path,
                "hash": file.hash,
                "numParts": len(file.parts),
            }
            for file in files
        ],
    }
    return body


def _trim_etag(value: str) -> str:
    return value.strip().strip('"')


def _format_bytes(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


class UploadProgressTracker:
    def __init__(
        self,
        *,
        total_bytes: int,
        total_parts: int,
        total_files: int,
        enabled: bool,
    ) -> None:
        self.enabled = enabled
        self.total_bytes = total_bytes
        self.total_parts = total_parts
        self.total_files = total_files
        self.uploaded_bytes = 0
        self.completed_parts = 0
        self.completed_files = 0
        self._lock = asyncio.Lock()
        self._progress: Progress | None = None
        self._bytes_task: TaskID | None = None
        self._parts_task: TaskID | None = None
        self._files_task: TaskID | None = None

    @classmethod
    def from_upload_plan(
        cls,
        local_files: list[LocalFile],
        remote_files: list[dict[str, Any]],
        *,
        enabled: bool,
    ) -> UploadProgressTracker:
        local_by_path = {file.path: file for file in local_files}
        total_bytes = 0
        total_parts = 0
        total_files = 0
        for remote_file in remote_files:
            if remote_file.get("skipUpload"):
                continue
            path = str(remote_file.get("path", ""))
            local_file = local_by_path[path]
            total_bytes += local_file.size
            total_parts += len(local_file.parts)
            total_files += 1
        return cls(
            total_bytes=total_bytes,
            total_parts=total_parts,
            total_files=total_files,
            enabled=enabled,
        )

    def __enter__(self) -> UploadProgressTracker:
        if not self.enabled:
            return self
        self._progress = Progress(
            SpinnerColumn(style="bar.pulse"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="bar.complete", complete_style="bar.finished"),
            TaskProgressColumn(),
            TextColumn("•"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console,
        )
        self._progress.start()
        self._bytes_task = self._progress.add_task("Overall", total=max(self.total_bytes, 1))
        self._parts_task = self._progress.add_task(
            f"Parts (0/{self.total_parts})",
            total=max(self.total_parts, 1),
        )
        self._files_task = self._progress.add_task(
            f"Files (0/{self.total_files})",
            total=max(self.total_files, 1),
        )
        return self

    def __exit__(self, *_args: object) -> None:
        if self._progress is not None:
            self._progress.stop()

    async def part_completed(
        self,
        *,
        file_path: str,
        part_number: int,
        total_file_parts: int,
        bytes_count: int,
    ) -> None:
        async with self._lock:
            self.uploaded_bytes += bytes_count
            self.completed_parts += 1
            if not self.enabled or self._progress is None:
                return
            assert self._bytes_task is not None
            assert self._parts_task is not None
            self._progress.update(self._bytes_task, completed=self.uploaded_bytes)
            self._progress.update(
                self._parts_task,
                completed=self.completed_parts,
                description=f"Parts ({self.completed_parts}/{self.total_parts})",
            )
            self._progress.console.print(
                f"[success]✓[/success] {file_path} part {part_number}/{total_file_parts} ({_format_bytes(bytes_count)})"
            )

    async def file_completed(self, file_path: str) -> None:
        async with self._lock:
            self.completed_files += 1
            if not self.enabled or self._progress is None:
                return
            assert self._files_task is not None
            self._progress.update(
                self._files_task,
                completed=self.completed_files,
                description=f"Files ({self.completed_files}/{self.total_files})",
            )
            self._progress.console.print(f"[success]✓[/success] {file_path} complete")


async def _read_file_part(path: Path, offset: int, size: int, chunk_size: int = 1024 * 1024) -> AsyncIterator[bytes]:
    with path.open("rb") as file:
        file.seek(offset)
        remaining = size
        while remaining > 0:
            chunk = await asyncio.to_thread(file.read, min(chunk_size, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


async def _upload_part(
    http_client: httpx.AsyncClient,
    *,
    local_file: LocalFile,
    local_part: LocalPart,
    remote_part: dict[str, Any],
    progress: UploadProgressTracker | None = None,
) -> dict[str, Any]:
    part_number = int(remote_part["partNumber"])
    headers = dict(cast(dict[str, str], remote_part.get("headers") or {}))
    headers["Content-Length"] = str(local_part.size)
    url = str(remote_part["url"])
    last_error: Exception | None = None

    for attempt in range(PART_UPLOAD_MAX_ATTEMPTS):
        try:
            response = await http_client.put(
                url,
                headers=headers,
                content=_read_file_part(local_file.abs_path, local_part.offset, local_part.size),
            )
            if response.status_code == httpx.codes.OK:
                etag = _trim_etag(response.headers.get("ETag", ""))
                if not etag:
                    raise ValueError(f"missing ETag for part {part_number}")
                if progress is not None:
                    await progress.part_completed(
                        file_path=local_file.path,
                        part_number=part_number,
                        total_file_parts=len(local_file.parts),
                        bytes_count=local_part.size,
                    )
                return {"partNumber": part_number, "hash": etag}
            response_text = response.text
            if 400 <= response.status_code < 500 and response.status_code != httpx.codes.TOO_MANY_REQUESTS:
                raise ValueError(f"upload status {response.status_code}: {response_text}")
            last_error = ValueError(f"upload status {response.status_code}: {response_text}")
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc
            if isinstance(exc, ValueError) and str(exc).startswith("upload status 4"):
                raise

        if attempt < PART_UPLOAD_MAX_ATTEMPTS - 1:
            await asyncio.sleep(2**attempt)

    assert last_error is not None
    raise ValueError(f"upload after retries: {last_error}") from last_error


async def _upload_file(
    http_client: httpx.AsyncClient,
    part_semaphore: asyncio.Semaphore,
    local_file: LocalFile,
    remote_file: dict[str, Any],
    progress: UploadProgressTracker | None = None,
) -> dict[str, Any]:
    remote_parts = list(cast(list[dict[str, Any]], remote_file.get("parts") or []))
    if len(local_file.parts) != len(remote_parts):
        raise ValueError(
            f"part count mismatch for {local_file.path}: local={len(local_file.parts)} remote={len(remote_parts)}"
        )

    local_parts_by_number = {part.number: part for part in local_file.parts}

    async def upload_remote_part(remote_part: dict[str, Any]) -> dict[str, Any]:
        part_number = int(remote_part["partNumber"])
        try:
            local_part = local_parts_by_number[part_number]
        except KeyError as exc:
            raise ValueError(f"server returned unknown part {part_number} for {local_file.path}") from exc
        async with part_semaphore:
            return await _upload_part(
                http_client,
                local_file=local_file,
                local_part=local_part,
                remote_part=remote_part,
                progress=progress,
            )

    completed_parts = await asyncio.gather(*(upload_remote_part(part) for part in remote_parts))
    if progress is not None:
        await progress.file_completed(local_file.path)
    return {
        "path": local_file.path,
        "hash": local_file.hash,
        "uploadDetails": {
            "uploadId": remote_file.get("uploadId", ""),
            "parts": sorted(completed_parts, key=lambda part: int(part["partNumber"])),
        },
    }


async def _upload_files(
    local_files: list[LocalFile],
    remote_files: list[dict[str, Any]],
    *,
    progress: UploadProgressTracker | None = None,
) -> list[dict[str, Any]]:
    local_by_path = {file.path: file for file in local_files}
    skipped: list[dict[str, Any]] = []
    to_upload: list[tuple[LocalFile, dict[str, Any]]] = []

    for remote_file in remote_files:
        path = str(remote_file.get("path", ""))
        try:
            local_file = local_by_path[path]
        except KeyError as exc:
            raise ValueError(f"server returned unknown file: {path}") from exc

        if remote_file.get("skipUpload"):
            skipped.append({"path": path, "hash": local_file.hash, "skipUpload": True})
        else:
            to_upload.append((local_file, remote_file))

    file_semaphore = asyncio.Semaphore(FILE_CONCURRENCY)
    part_semaphore = asyncio.Semaphore(PART_CONCURRENCY)
    timeout = httpx.Timeout(PART_UPLOAD_TIMEOUT_SECONDS)

    async with httpx.AsyncClient(timeout=timeout) as http_client:

        async def upload_one(local_file: LocalFile, remote_file: dict[str, Any]) -> dict[str, Any]:
            async with file_semaphore:
                return await _upload_file(
                    http_client,
                    part_semaphore,
                    local_file,
                    remote_file,
                    progress=progress,
                )

        uploaded = await asyncio.gather(*(upload_one(local_file, remote_file) for local_file, remote_file in to_upload))

    return [*skipped, *uploaded]


async def _upload_model_files(
    *,
    config: CLIConfig,
    local_path: Path,
    object_id: str,
    show_progress: bool = False,
) -> str:
    if show_progress:
        with console.status(
            "[progress.description]Preparing files (computing hashes)...[/progress.description]",
            spinner="dots",
            spinner_style="bar.pulse",
        ):
            local_files = await _prepare_files(local_path)
    else:
        local_files = await _prepare_files(local_path)
    if not local_files:
        raise ValueError("no files to upload")

    create_response = cast(
        dict[str, Any],
        await config.client.post(
            path_template(
                "/projects/{project_id}/models/upload/create",
                project_id=config.client._get_project_id_path_param(),
            ),
            cast_to=object,
            body=_create_upload_body(
                object_id=object_id,
                files=local_files,
            ),
        ),
    )

    remote_files = list(cast(list[dict[str, Any]], create_response.get("files") or []))
    progress = UploadProgressTracker.from_upload_plan(
        local_files,
        remote_files,
        enabled=show_progress,
    )
    if show_progress and progress.total_files > 0:
        console.print(
            f"Uploading {progress.total_files} file(s), "
            f"{progress.total_parts} part(s), "
            f"{_format_bytes(progress.total_bytes)} total"
        )
    with progress:
        complete_files = await _upload_files(local_files, remote_files, progress=progress)
    complete_response = cast(
        dict[str, Any],
        await config.client.post(
            path_template(
                "/projects/{project_id}/models/upload/complete",
                project_id=config.client._get_project_id_path_param(),
            ),
            cast_to=object,
            body={
                "objectId": object_id,
                "files": complete_files,
            },
        ),
    )
    return str(complete_response.get("revisionId") or "")


async def upload(
    model_id: Annotated[str, Parameter(help="Existing model or adapter ID to upload files to")],
    local_path: Annotated[Path, Parameter(help="Local file or directory to upload")],
    *,
    config: CLIConfigParameter,
) -> None:
    """Upload files to a beta model or adapter."""

    await assert_explicit_project_id(config)

    source = Path(local_path)

    # Ensure we use the v2 apis for this
    config.client.base_url = "https://api.together.ai/v2"

    if config.json:
        revision_id = await _upload_model_files(
            config=config,
            local_path=source,
            object_id=model_id,
        )
        console.print_json(data={"revisionId": revision_id})
        return

    console.print(f"Uploading {source} to {model_id}...")
    try:
        revision_id = await _upload_model_files(
            config=config,
            local_path=source,
            object_id=model_id,
            show_progress=True,
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)
    console.print(f"Upload complete. Revision: {revision_id}")
