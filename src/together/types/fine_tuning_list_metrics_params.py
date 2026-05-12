# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FineTuningListMetricsParams"]


class FineTuningListMetricsParams(TypedDict, total=False):
    global_step_from: int
    """Return only metrics with global_step >= this value."""

    global_step_to: int
    """Return only metrics with global_step <= this value."""

    logged_at_from: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Return only metrics logged at or after this ISO-8601 timestamp."""

    logged_at_to: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Return only metrics logged at or before this ISO-8601 timestamp."""

    resolution: int
    """Number of (uniformly sampled) train metrics to return."""
