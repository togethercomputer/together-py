from __future__ import annotations

import time
import asyncio
from typing import Optional, Annotated
from pathlib import Path

from cyclopts import Parameter, validators

from together._exceptions import APIError, RateLimitError, APIConnectionError, InternalServerError
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.types.post_training import QuantizationJob, QuantizationEstimate
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console, error_console
from together.lib.cli.components.upload_progress import upload_file_with_progress
from together.types.post_training.quantization_event import QuantizationEvent
from together.types.post_training.prepare_for_fp4_inference_create_params import Inputs

TERMINAL_STATUSES = ("completed", "cancelled", "error", "user_error")
FAILED_STATUSES = ("error", "user_error")
NON_CANCELLABLE_STATUSES = ("cancel_requested", *TERMINAL_STATUSES)

STATUS_COLORS = {
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "cancel_requested": "yellow",
    "cancelled": "red",
    "error": "red",
    "user_error": "red",
    "completed": "green",
}

_EVENT_LEVEL_COLORS = {"Info": "dim", "Warning": "yellow", "Error": "red"}

DEFAULT_POLL_INTERVAL_SECONDS = 10.0

# Errors a long --watch should ride out rather than abort on; the CLI client makes no retries of its own.
_TRANSIENT_ERRORS = (APIConnectionError, InternalServerError, RateLimitError)
_MAX_RETRY_DELAY_SECONDS = 60.0
# Consecutive failing time after which --watch gives up and prints the resume command.
_MAX_TRANSIENT_FAILURE_SECONDS = 300.0

AdapterRevisionParameter = Annotated[
    Optional[str],
    Parameter(
        name="--adapter-revision-id", alias="-r", help="Adapter revision ID; defaults to the adapter's current revision"
    ),
]
PollIntervalParameter = Annotated[
    float,
    Parameter(
        name="--poll-interval",
        help="Seconds between status checks when --watch is set",
        validator=validators.Number(gt=0),
    ),
]
CalibrationFileParameter = Annotated[
    Optional[str],
    Parameter(
        name="--calibration-file",
        alias="-c",
        help=(
            "Conversation dataset (JSONL rows with `messages`, optionally `tools`; at most 64 MiB) "
            "used for half of the calibration corpus: a Files API ID or a local path to upload"
        ),
    ),
]


def build_inputs(
    adapter_object_id: str,
    adapter_revision_id: Optional[str],
    calibration_file_id: Optional[str],
) -> Inputs:
    inputs: Inputs = {"adapter_object_id": adapter_object_id}
    if adapter_revision_id is not None:
        inputs["adapter_revision_id"] = adapter_revision_id
    if calibration_file_id is not None:
        inputs["calibration_file_id"] = calibration_file_id
    return inputs


async def resolve_calibration_file(calibration_file: Optional[str], config: CLIConfig) -> Optional[str]:
    """Return a Files API ID, uploading ``calibration_file`` first when it is a local path."""
    if calibration_file is None:
        return None
    path = Path(calibration_file)
    if path.is_dir():
        raise ValueError(f"Path {calibration_file} is a directory, not a file. Please provide a file path.")
    if not path.is_file():
        # Files API IDs are bare tokens; anything shaped like a path is a local file that is missing.
        looks_like_path = bool(path.suffix) or len(path.parts) > 1
        if looks_like_path:
            raise ValueError(f"Calibration file {calibration_file} does not exist.")
        return calibration_file
    # Uploads are idempotent, so re-running the command reuses the same file ID.
    uploaded = await upload_file_with_progress(
        config.client.files.upload,
        path,
        enabled=not config.json,
        description=f"Uploading calibration file {path.name}",
        purpose="calibration",
    )
    return uploaded.id


def format_status(status: str) -> str:
    color = STATUS_COLORS.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def format_estimate(estimate: QuantizationEstimate) -> str:
    return (
        f"The estimated price of this job is [bold]${estimate.price_usd:,.2f}[/bold] "
        f"and it is expected to run for about [bold]{estimate.time_hours:.1f}h[/bold] (excluding queue time)."
    )


def format_credit_warning(estimate: QuantizationEstimate) -> str:
    return (
        "[yellow][bold]The estimated price exceeds your available credit "
        f"(limit ${estimate.credit_limit:,.2f}).[/bold][/yellow] The job will likely be rejected. "
        "Consider increasing your credit limit at https://api.together.ai/settings/profile"
    )


def format_event(event: QuantizationEvent) -> str:
    color = _EVENT_LEVEL_COLORS.get(event.level, "white")
    return f"  [dim]{format_datetime(event.created_at)}[/dim]  [{color}]{event.message}[/{color}]"


def _print_next_steps(job: QuantizationJob) -> None:
    if job.status == "completed" and job.results is not None and job.results.api_model_object_id is not None:
        console.print(f"\n  Prepared model: [primary]{job.results.api_model_object_id}[/primary]")
        if job.results.api_model_revision_id is not None:
            console.print(f"  Revision: [primary]{job.results.api_model_revision_id}[/primary]")
    elif job.status not in TERMINAL_STATUSES:
        console.print("\n  You can track the job's progress with the following command:")
        console.print(f"  [dim]-[/dim] [primary]tg training fp4 get {job.id} --watch[/primary]")


def _print_resume_hint(job_id: str) -> None:
    console.print("\n  Stopped watching; the job keeps running. Resume with:")
    console.print(f"  [dim]-[/dim] [primary]tg training fp4 get {job_id} --watch[/primary]")


async def watch_job(job_id: str, config: CLIConfig, poll_interval: float) -> QuantizationJob:
    """Poll a job until it reaches a terminal status, printing each new event once.

    Transient API errors are retried with exponential backoff (honoring a 429's
    Retry-After) for up to five minutes of consecutive failures before the error is raised.
    """
    seen: set[tuple[object, ...]] = set()
    last_status: Optional[str] = None
    has_polled = False
    failing_since: Optional[float] = None
    retry_delay = min(poll_interval, _MAX_RETRY_DELAY_SECONDS)
    while True:
        try:
            job = await config.client.post_training.prepare_for_fp4_inference.retrieve(job_id)
        except _TRANSIENT_ERRORS as error:
            now = time.monotonic()
            if failing_since is None:
                failing_since = now
            if now - failing_since >= _MAX_TRANSIENT_FAILURE_SECONDS:
                if has_polled and not config.json:
                    _print_resume_hint(job_id)
                raise
            delay = retry_delay
            if isinstance(error, RateLimitError):
                retry_after = config.client._parse_retry_after_header(error.response.headers)
                if retry_after is not None:
                    # Capped like the SDK's own retries, so one header cannot stall --watch past its budget.
                    delay = max(delay, min(retry_after, _MAX_RETRY_DELAY_SECONDS))
            error_console.print(f"[dim]API request failed ({type(error).__name__}); retrying in {delay:.3g}s...[/dim]")
            await asyncio.sleep(delay)
            retry_delay = min(retry_delay * 2, _MAX_RETRY_DELAY_SECONDS)
            continue
        except APIError:
            # Before the first successful poll the job may not exist or be readable, so no resume advice.
            if has_polled and not config.json:
                _print_resume_hint(job_id)
            raise
        has_polled = True
        failing_since = None
        retry_delay = min(poll_interval, _MAX_RETRY_DELAY_SECONDS)
        if not config.json:
            if job.status != last_status:
                console.print(f"Status: {format_status(job.status)}")
                last_status = job.status
            for event in sorted(job.events, key=lambda e: e.created_at):
                key = (event.hash, event.created_at, event.type, event.message)
                if key not in seen:
                    seen.add(key)
                    console.print(format_event(event))
        if job.status in TERMINAL_STATUSES:
            return job
        await asyncio.sleep(poll_interval)


def report_job(job: QuantizationJob, config: CLIConfig) -> None:
    """Print the job (JSON or next steps), exiting non-zero if it failed."""
    if config.json:
        console.print_json(openapi_dumps(job).decode("utf-8"))
    else:
        _print_next_steps(job)

    if job.status in FAILED_STATUSES:
        if not config.json:
            console.print(f"\n[red]x[/red] Job finished with status {format_status(job.status)}")
        raise CliDiagnosticExit(f"FP4 preparation job failed ({job.status})")
