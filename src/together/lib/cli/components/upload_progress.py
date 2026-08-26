from __future__ import annotations

import asyncio
from pprint import pformat
from typing import Any, TypeVar, Callable, Awaitable
from pathlib import Path
from collections.abc import Sequence

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

from together.lib import FileTypeError, check_file
from together.lib.resources.files import FileUploadProgress, UploadProgressCallback
from together.lib.cli.utils._console import console
from together.lib.cli.components.check_progress import CheckProgressTracker, should_show_check_progress

T = TypeVar("T")


def format_bytes(num: int) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


class UploadProgressTracker:
    """Shared Rich progress tracker for CLI file uploads."""

    def __init__(
        self,
        *,
        total_bytes: int,
        total_parts: int,
        total_files: int,
        enabled: bool,
        description: str = "Overall",
        show_parts: bool = True,
        show_files: bool = True,
    ) -> None:
        self.enabled = enabled
        self.total_bytes = total_bytes
        self.total_parts = total_parts
        self.total_files = total_files
        self.description = description
        self.show_parts = show_parts
        self.show_files = show_files
        self.uploaded_bytes = 0
        self.completed_parts = 0
        self.completed_files = 0
        self._lock = asyncio.Lock()
        self._progress: Progress | None = None
        self._bytes_task: TaskID | None = None
        self._parts_task: TaskID | None = None
        self._files_task: TaskID | None = None

    @classmethod
    def for_single_file(
        cls,
        file: Path,
        *,
        enabled: bool,
        description: str | None = None,
    ) -> UploadProgressTracker:
        return cls(
            total_bytes=max(file.stat().st_size, 0),
            total_parts=1,
            total_files=1,
            enabled=enabled,
            description=description or f"Uploading {file.name}",
            show_parts=False,
            show_files=False,
        )

    @classmethod
    def from_upload_plan(
        cls,
        local_files: Sequence[Any],
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
        if not self.enabled or not console.is_terminal:
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
            transient=True,
        )
        self._progress.start()
        self._bytes_task = self._progress.add_task(self.description, total=max(self.total_bytes, 1))
        if self.show_parts:
            self._parts_task = self._progress.add_task(
                f"Parts (0/{self.total_parts})",
                total=max(self.total_parts, 1),
            )
        if self.show_files:
            self._files_task = self._progress.add_task(
                f"Files (0/{self.total_files})",
                total=max(self.total_files, 1),
            )
        return self

    def __exit__(self, *_args: object) -> None:
        if self._progress is not None:
            self._progress.stop()

    def set_uploaded_bytes(self, uploaded_bytes: int) -> None:
        """Sync update used by SDK upload progress callbacks."""

        self.uploaded_bytes = uploaded_bytes
        if not self.enabled or self._progress is None or self._bytes_task is None:
            return
        self._progress.update(self._bytes_task, completed=min(uploaded_bytes, max(self.total_bytes, 1)))

    def as_callback(self) -> UploadProgressCallback | None:
        if not self.enabled:
            return None

        def on_progress(event: FileUploadProgress) -> None:
            self.set_uploaded_bytes(event.uploaded_bytes)

        return on_progress

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
            self._progress.update(self._bytes_task, completed=self.uploaded_bytes)
            if self.show_parts:
                assert self._parts_task is not None
                self._progress.update(
                    self._parts_task,
                    completed=self.completed_parts,
                    description=f"Parts ({self.completed_parts}/{self.total_parts})",
                )
                self._progress.console.print(
                    f"[success]✓[/success] {file_path} part {part_number}/{total_file_parts} "
                    f"({format_bytes(bytes_count)})"
                )

    async def file_completed(self, file_path: str) -> None:
        async with self._lock:
            self.completed_files += 1
            if not self.enabled or self._progress is None:
                return
            if self.show_files:
                assert self._files_task is not None
                self._progress.update(
                    self._files_task,
                    completed=self.completed_files,
                    description=f"Files ({self.completed_files}/{self.total_files})",
                )
                self._progress.console.print(f"[success]✓[/success] {file_path} complete")


async def upload_file_with_progress(
    upload: Callable[..., Awaitable[T]],
    file: Path,
    *,
    enabled: bool = True,
    description: str | None = None,
    check: bool = True,
    purpose: str = "fine-tune",
    **upload_kwargs: object,
) -> T:
    """Run an async file upload while optionally rendering shared Rich progress.

    Validation runs *before* the upload bar starts so a multi-GB ``check_file``
    pass isn't shown as a stuck 0% upload.
    """

    if check:
        with CheckProgressTracker(
            file, enabled=should_show_check_progress(file, json_mode=not enabled)
        ) as check_tracker:
            report = check_file(
                file,
                purpose=purpose,
                progress_callback=check_tracker.as_callback(),
            )
        if report["is_check_passed"] is False:
            raise FileTypeError(f"Invalid file supplied, failed to upload. Report:\n{pformat(report)}")

    with UploadProgressTracker.for_single_file(file, enabled=enabled, description=description) as tracker:
        return await upload(
            file=file,
            progress_callback=tracker.as_callback(),
            check=False,
            purpose=purpose,
            **upload_kwargs,
        )
