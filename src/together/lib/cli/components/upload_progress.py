from __future__ import annotations

from typing import TypeVar, Callable, Awaitable
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Iterator

from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    DownloadColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from together.lib.resources.files import FileUploadProgress, UploadProgressCallback
from together.lib.cli.utils._console import console

T = TypeVar("T")


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

    with Progress(
        SpinnerColumn(style="bar.pulse"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="bar.complete", complete_style="bar.finished"),
        TaskProgressColumn(),
        TextColumn("•"),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task(task_description, total=total_bytes)

        def on_progress(event: FileUploadProgress) -> None:
            progress.update(task_id, completed=min(event.uploaded_bytes, total_bytes))

        yield on_progress


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
