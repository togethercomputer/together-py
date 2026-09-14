from __future__ import annotations

from typing import Literal
from typing_extensions import TypeAlias

from rich.markup import escape as escape_rich_markup

from together.lib.utils.tools import format_datetime
from together.types.batch_job import BatchJob
from together.lib.cli.utils._console import console

BatchApiType: TypeAlias = Literal["chat.completions", "audio.transcriptions", "audio.translations"]
BatchEndpoint: TypeAlias = Literal["/v1/chat/completions", "/v1/audio/transcriptions", "/v1/audio/translations"]

API_TO_ENDPOINT: dict[BatchApiType, BatchEndpoint] = {
    "chat.completions": "/v1/chat/completions",
    "audio.transcriptions": "/v1/audio/transcriptions",
    "audio.translations": "/v1/audio/translations",
}

ENDPOINT_TO_API: dict[str, BatchApiType] = {endpoint: api for api, endpoint in API_TO_ENDPOINT.items()}

STATUS_COLORS = {
    "VALIDATING": "yellow",
    "IN_PROGRESS": "yellow",
    "COMPLETED": "green",
    "FAILED": "red",
    "EXPIRED": "red",
    "CANCELLED": "red",
}

_INCOMPLETE_STATUSES = frozenset({"VALIDATING", "IN_PROGRESS"})
_DOWNLOADABLE_STATUSES = frozenset({"COMPLETED", "FAILED", "EXPIRED", "CANCELLED"})
_PROGRESS_BAR_WIDTH = 20


def format_endpoint(endpoint: str | None) -> str:
    if not endpoint:
        return ""
    return ENDPOINT_TO_API.get(endpoint, endpoint)


def format_status(status: str | None) -> str:
    if not status:
        return ""
    color = STATUS_COLORS.get(status, "white")
    return f"[bold {color}]{status.capitalize()}[/bold {color}]"


def format_progress(progress: float) -> str:
    pct = max(0.0, min(100.0, progress))
    filled = round((pct / 100.0) * _PROGRESS_BAR_WIDTH)
    bar = "█" * filled + "░" * (_PROGRESS_BAR_WIDTH - filled)
    return f"[yellow]{bar}[/yellow] [bold]{pct:g}%[/bold]"


def print_batch_detail(job: BatchJob) -> None:
    """Print a curated human-readable view of a batch job."""
    console.print("Batch job details:")
    if job.created_at:
        console.print(f" - Created at {format_datetime(job.created_at)}")
    if job.status == "COMPLETED" and job.completed_at:
        console.print(f" - Completed at {format_datetime(job.completed_at)}")

    api = format_endpoint(job.endpoint)
    if api:
        console.print(f" - {api}")

    if job.x_model_id:
        console.print(f" - {job.x_model_id}")

    if job.output_file_id:
        console.print(f" - Output file ID {job.output_file_id}")

    if job.error_file_id or job.error:
        console.print(" - [red]An error occurred[/red]")
        if job.error_file_id:
            console.print(f" - Error file ID {job.error_file_id}")
        if job.error:
            console.print(f"   {escape_rich_markup(job.error)}")

    if job.status:
        if job.status in _INCOMPLETE_STATUSES and job.progress is not None:
            console.print(f"{format_progress(job.progress)} {format_status(job.status)}")
        else:
            console.print(format_status(job.status))

    if job.status in _DOWNLOADABLE_STATUSES and job.id and (job.output_file_id or job.error_file_id):
        console.print("\nDownload results with:")
        console.print(f"[dim]-[/dim] [primary]tg batches download {job.id} --output ./out[/primary]")
