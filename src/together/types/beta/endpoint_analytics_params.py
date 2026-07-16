# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EndpointAnalyticsParams"]


class EndpointAnalyticsParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """Restrict to a single deployment under this endpoint."""

    end_time: Annotated[Union[str, datetime], PropertyInfo(alias="endTime", format="iso8601")]
    """Exclusive end of the time range. Defaults to now if unset."""

    granularity: str
    """Time-series bucket duration, such as `1m`, `1h`, or `1d`. Defaults to `1d`."""

    include_time_series: Annotated[bool, PropertyInfo(alias="includeTimeSeries")]
    """When true, include per-bucket time series in the response."""

    start_time: Annotated[Union[str, datetime], PropertyInfo(alias="startTime", format="iso8601")]
    """Inclusive start of the time range. Defaults to 24 hours ago if unset."""
