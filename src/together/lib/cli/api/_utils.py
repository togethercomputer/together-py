from __future__ import annotations

import re
import math
from typing import Any, List, Union, Literal, Sequence
from datetime import datetime

from cyclopts import Parameter

from together.lib.utils.tools import localize_datetime
from together.lib.types.fine_tuning import COMPLETED_STATUSES, FinetuneResponse
from together.types.finetune_response import FinetuneResponse as _FinetuneResponse
from together.types.fine_tuning_list_response import Data

_PROGRESS_BAR_WIDTH = 40


def _int_or_max_converter(_type: type, tokens: Sequence[Any]) -> int | Literal["max"]:
    val = tokens[0].value if tokens else ""
    if val == "max":
        return "max"
    try:
        return int(val)
    except ValueError as e:
        raise ValueError(f"{val!r} is not a valid integer or 'max'.") from e


@Parameter(converter="parse")
class BoolOrAuto:
    value: Literal["auto", True, False]

    def __init__(self, value: Literal["auto", True, False]):
        self.value = value

    help_name = "true, false, auto"

    @Parameter(accepts_keys=False, n_tokens=1)
    @classmethod
    def parse(cls, tokens: Sequence[Any]) -> BoolOrAuto:
        """Parse a coordinate string like '10,20' into a Point.

        Note: classmethod signature is (cls, tokens), not (type_, tokens)
        """
        val = tokens[0].value if tokens else ""
        if val == "auto":
            return cls("auto")
        if val.lower() in ("true", "1", "yes"):
            return cls(True)
        if val.lower() in ("false", "0", "no"):
            return cls(False)
        raise ValueError(f"{val!r} is not a boolean or 'auto'.")


# For use in fine_tuning create (batch_size, train_on_inputs)
int_or_max_converter = _int_or_max_converter


def _human_readable_time(timedelta: float) -> str:
    """Convert a timedelta to a compact human-readble string
    Examples:
        00:00:10 -> 10s
        01:23:45 -> 1h 23min 45s
        1 Month 23 days 04:56:07 -> 1month 23d 4h 56min 7s
    Args:
        timedelta (float): The timedelta in seconds to convert.
    Returns:
        A string representing the timedelta in a human-readable format.
    """
    units = [
        (30 * 24 * 60 * 60, "month"),  # 30 days
        (24 * 60 * 60, "d"),
        (60 * 60, "h"),
        (60, "min"),
        (1, "s"),
    ]

    total_seconds = int(timedelta)
    parts: List[str] = []

    for unit_seconds, unit_name in units:
        if total_seconds >= unit_seconds:
            value = total_seconds // unit_seconds
            total_seconds %= unit_seconds
            parts.append(f"{value}{unit_name}")

    return " ".join(parts) if parts else "0s"


def generate_progress_text(
    finetune_job: Union[Data, FinetuneResponse, _FinetuneResponse], current_time: datetime
) -> str:
    """Generate a progress text for a finetune job.
    Args:
        finetune_job: The finetune job to generate a progress text for.
        current_time: The current time.
    Returns:
        A string representing the progress text.
    """
    time_text = ""
    if getattr(finetune_job, "started_at", None) is not None and isinstance(finetune_job.started_at, datetime):
        started_at = localize_datetime(finetune_job.started_at)

        if finetune_job.progress is not None:
            if current_time < started_at:
                return ""

            if not finetune_job.progress.estimate_available:
                return ""

            if finetune_job.progress.seconds_remaining <= 0:
                return ""

            elapsed_time = (current_time - started_at).total_seconds()
            time_left = "N/A"
            if finetune_job.progress.seconds_remaining > elapsed_time:
                time_left = _human_readable_time(finetune_job.progress.seconds_remaining - elapsed_time)
            time_text = f"{time_left} left"
    return time_text


def generate_progress_bar(
    finetune_job: Union[Data, FinetuneResponse, _FinetuneResponse], current_time: datetime, use_rich: bool = False
) -> str:
    """Generate a progress bar for a finetune job.
    Args:
        finetune_job: The finetune job to generate a progress bar for.
        current_time: The current time.
        use_rich: Whether to use rich formatting.
    Returns:
        A string representing the progress bar.
    """
    progress = "Progress: [bold red]unavailable[/bold red]"
    if finetune_job.status in COMPLETED_STATUSES:
        progress = "Progress: [bold green]completed[/bold green]"
    elif getattr(finetune_job, "started_at", None) is not None and isinstance(finetune_job.started_at, datetime):
        started_at = localize_datetime(finetune_job.started_at)

        if finetune_job.progress is not None:
            if current_time < started_at:
                return progress

            if not finetune_job.progress.estimate_available:
                return progress

            if finetune_job.progress.seconds_remaining <= 0:
                return progress

            elapsed_time = (current_time - started_at).total_seconds()
            ratio_filled = min(elapsed_time / finetune_job.progress.seconds_remaining, 1.0)
            percentage = ratio_filled * 100
            filled = math.ceil(ratio_filled * _PROGRESS_BAR_WIDTH)
            bar = "█" * filled + "░" * (_PROGRESS_BAR_WIDTH - filled)
            time_text = generate_progress_text(finetune_job, current_time)
            progress = f"Progress: {bar} [bold]{percentage:>3.0f}%[/bold] [yellow]{time_text}[/yellow]"

    if use_rich:
        return progress

    return re.sub(r"\[/?[^\]]+\]", "", progress)
