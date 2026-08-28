from __future__ import annotations

import asyncio

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

from together.lib.resources.files import FileDownloadProgress, DownloadProgressCallback
from together.lib.cli.utils._console import console


class DownloadProgressTracker:
    """Shared Rich progress tracker for CLI file downloads."""

    def __init__(
        self,
        *,
        total_bytes: int,
        total_files: int,
        enabled: bool,
        description: str = "Overall",
        show_files: bool = True,
    ) -> None:
        self.enabled = enabled
        self.total_bytes = total_bytes
        self.total_files = total_files
        self.description = description
        self.show_files = show_files
        self.downloaded_bytes = 0
        self.completed_files = 0
        self.skipped_files = 0
        self._lock = asyncio.Lock()
        self._progress: Progress | None = None
        self._bytes_task: TaskID | None = None
        self._files_task: TaskID | None = None

    @classmethod
    def for_single_file(
        cls,
        *,
        enabled: bool,
        description: str = "Downloading file",
        total_bytes: int = 0,
    ) -> DownloadProgressTracker:
        return cls(
            total_bytes=total_bytes,
            total_files=1,
            enabled=enabled,
            description=description,
            show_files=False,
        )

    def __enter__(self) -> DownloadProgressTracker:
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
        if self.show_files:
            self._files_task = self._progress.add_task(
                f"Files (0/{self.total_files})",
                total=max(self.total_files, 1),
            )
        return self

    def __exit__(self, *_args: object) -> None:
        if self._progress is not None:
            self._progress.stop()

    def set_downloaded_bytes(self, downloaded_bytes: int, *, total_bytes: int | None = None) -> None:
        """Sync update used by SDK download progress callbacks."""

        if total_bytes is not None and total_bytes > 0 and total_bytes != self.total_bytes:
            self.total_bytes = total_bytes
            if self._progress is not None and self._bytes_task is not None:
                self._progress.update(self._bytes_task, total=max(total_bytes, 1))
        self.downloaded_bytes = downloaded_bytes
        if not self.enabled or self._progress is None or self._bytes_task is None:
            return
        self._progress.update(self._bytes_task, completed=min(downloaded_bytes, max(self.total_bytes, 1)))

    def as_callback(self) -> DownloadProgressCallback | None:
        if not self.enabled:
            return None

        def on_progress(event: FileDownloadProgress) -> None:
            self.set_downloaded_bytes(event.downloaded_bytes, total_bytes=event.total_bytes)

        return on_progress

    async def bytes_completed(self, count: int) -> None:
        async with self._lock:
            self.downloaded_bytes += count
            if not self.enabled or self._progress is None:
                return
            assert self._bytes_task is not None
            self._progress.update(self._bytes_task, completed=self.downloaded_bytes)

    async def file_completed(self, file_path: str, *, skipped: bool = False) -> None:
        async with self._lock:
            self.completed_files += 1
            if skipped:
                self.skipped_files += 1
            if not self.enabled or self._progress is None:
                return
            if self.show_files:
                assert self._files_task is not None
                self._progress.update(
                    self._files_task,
                    completed=self.completed_files,
                    description=f"Files ({self.completed_files}/{self.total_files})",
                )
                if skipped:
                    self._progress.console.print(f"[dim]↷[/dim] {file_path} skipped (already exists)")
                else:
                    self._progress.console.print(f"[success]✓[/success] {file_path} complete")
