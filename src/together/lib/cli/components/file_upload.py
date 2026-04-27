from __future__ import annotations

from pathlib import Path

from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

from together import AsyncTogether
from together.types import FilePurpose
from together.types.file_response import FileResponse
from together.lib.cli.utils._console import console


async def files_upload_with_rich_progress(
    client: AsyncTogether,
    file: Path,
    purpose: FilePurpose,
    *,
    check: bool = True,
    description: str = "Uploading",
) -> FileResponse:
    """
    Run ``client.files.upload`` with Rich progress using the same default column
    stack as :func:`rich.progress.track` (``TextColumn``, ``BarColumn``,
    ``TaskProgressColumn``, ``TimeRemainingColumn``). The upload is driven by a
    bytes callback, so we use :class:`~rich.progress.Progress` and
    :meth:`~rich.progress.Progress.update` rather than iterating ``track()``.
    """
    fsize = max(file.stat().st_size, 1)
    label = f"{description} {file.name}"
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        TimeRemainingColumn(elapsed_when_finished=True),
        console=console,
        transient=True,
        refresh_per_second=10,
    ) as progress:
        task = progress.add_task(label, total=fsize)

        return await client.files.upload(file, purpose=purpose, check=check, callback=lambda n: progress.update(task, completed=min(n, fsize), total=fsize))
