from __future__ import annotations

from pathlib import Path

from rich.progress import (
    TaskID,
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    DownloadColumn,
    TaskProgressColumn,
)

from together.lib.utils.files import FileCheckProgress, CheckProgressCallback
from together.lib.cli.utils._console import console

_PHASE_DESCRIPTIONS = {
    "utf8": "Checking encoding",
    "jsonl": "Validating JSONL",
    "csv": "Validating CSV",
    "parquet": "Validating Parquet",
}
# Tiny files finish instantly; don't pay for a live display (or pollute CLI tests).
CHECK_PROGRESS_MIN_BYTES = 1024 * 1024
_TWO_PASS_SUFFIXES = {".jsonl", ".csv"}


def _expected_check_work_bytes(file: Path) -> int:
    """Total progress units for a check: two full scans for JSONL/CSV, one for everything else."""
    size = max(file.stat().st_size, 1)
    if file.suffix in _TWO_PASS_SUFFIXES:
        return size * 2
    return size


def should_show_check_progress(file: Path, *, json_mode: bool) -> bool:
    if json_mode or not console.is_terminal:
        return False
    try:
        return file.is_file() and file.stat().st_size >= CHECK_PROGRESS_MIN_BYTES
    except OSError:
        return False


class CheckProgressTracker:
    """Rich progress tracker for CLI ``files check`` / pre-upload validation."""

    def __init__(self, file: Path, *, enabled: bool) -> None:
        self.file = file
        self.enabled = enabled
        self._progress: Progress | None = None
        self._task: TaskID | None = None
        self._phase: str | None = None
        self._completed_phase_bytes = 0
        self._current_phase_total = 0
        self._total = 1

    def __enter__(self) -> CheckProgressTracker:
        if not self.enabled:
            return self
        total = _expected_check_work_bytes(self.file)
        self._total = total
        self._progress = Progress(
            SpinnerColumn(style="bar.pulse"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="bar.complete", complete_style="bar.finished"),
            TaskProgressColumn(),
            TextColumn("•"),
            DownloadColumn(),
            console=console,
            transient=True,
        )
        self._progress.start()
        self._task = self._progress.add_task(f"Checking {self.file.name}", total=total)
        return self

    def __exit__(self, *_args: object) -> None:
        if self._progress is not None:
            self._progress.stop()

    def as_callback(self) -> CheckProgressCallback | None:
        if not self.enabled:
            return None

        def on_progress(event: FileCheckProgress) -> None:
            if self._progress is None or self._task is None:
                return
            if event.phase != self._phase:
                if self._phase is not None:
                    self._completed_phase_bytes += self._current_phase_total
                self._phase = event.phase
                self._current_phase_total = event.total_bytes
            phase_label = _PHASE_DESCRIPTIONS.get(event.phase, "Checking")
            completed = self._completed_phase_bytes + event.processed_bytes
            self._progress.update(
                self._task,
                description=f"{phase_label} {self.file.name}",
                completed=min(completed, self._total),
            )

        return on_progress
