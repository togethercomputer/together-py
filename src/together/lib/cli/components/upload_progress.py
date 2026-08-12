from __future__ import annotations

from typing import TypeVar, Callable, Awaitable
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Iterator

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

from together.lib.resources.files import (
    FileUploadProgress,
    FileDownloadProgress,
    UploadProgressCallback,
    DownloadProgressCallback,
)
from together.lib.cli.utils._console import console

T = TypeVar("T")


def _make_transfer_progress() -> Progress:
    return Progress(
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


@contextmanager
def file_upload_progress(
    file: Path,
    *,
    enabled: bool = True,
    description: str | None = None,
) -> Iterator[UploadProgressCallback | None]:
    """Render rich progress for a file upload when enabled.

    Yields a progress callback for upload managers, or ``None`` when disabled.
    """

    if not enabled:
        yield None
        return

    total_bytes = max(file.stat().st_size, 1)
    task_description = description or f"Uploading {file.name}"

    with _make_transfer_progress() as progress:
        task_id = progress.add_task(task_description, total=total_bytes)

        def on_progress(event: FileUploadProgress) -> None:
            progress.update(task_id, completed=min(event.uploaded_bytes, total_bytes))

        yield on_progress


@contextmanager
def file_download_progress(
    *,
    enabled: bool = True,
    description: str = "Downloading file",
) -> Iterator[DownloadProgressCallback | None]:
    """Render rich progress for a file download when enabled.

    Task total is taken from the first progress event (metadata arrives mid-download).
    """

    if not enabled:
        yield None
        return

    progress = _make_transfer_progress()
    progress.start()
    task_id: TaskID | None = None

    def on_progress(event: FileDownloadProgress) -> None:
        nonlocal task_id
        if task_id is None:
            task_id = progress.add_task(description, total=max(event.total_bytes, 1))
        assert task_id is not None
        progress.update(task_id, completed=min(event.downloaded_bytes, max(event.total_bytes, 1)))

    try:
        yield on_progress
    finally:
        progress.stop()


async def upload_file_with_progress(
    upload: Callable[..., Awaitable[T]],
    file: Path,
    *,
    enabled: bool = True,
    description: str | None = None,
    **upload_kwargs: object,
) -> T:
    """Run an async file upload while optionally rendering rich progress."""

    with file_upload_progress(file, enabled=enabled, description=description) as progress_callback:
        return await upload(file=file, progress_callback=progress_callback, **upload_kwargs)
