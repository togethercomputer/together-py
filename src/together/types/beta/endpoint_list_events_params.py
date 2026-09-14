# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["EndpointListEventsParams"]


class EndpointListEventsParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous endpoint event list response."""

    deployment_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="deploymentIds")]
    """Deployment IDs whose events should be included.

    Every ID must belong to the endpoint. Supplying this filter excludes
    endpoint-scoped events unless `SOURCE_KIND_ENDPOINT` is also included in
    `sourceKinds`.
    """

    limit: int
    """Maximum number of events to return. Max 10000, defaults to 50."""

    min_level: Annotated[
        Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"], PropertyInfo(alias="minLevel")
    ]
    """Minimum severity. Omit to disable severity filtering."""

    since: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Return only events at or after this time."""

    source_kinds: Annotated[
        List[Literal["SOURCE_KIND_ENDPOINT", "SOURCE_KIND_DEPLOYMENT"]], PropertyInfo(alias="sourceKinds")
    ]
    """Resource kinds whose events should be included.

    Omit to include both endpoint- and deployment-scoped events.
    """

    subject_id: Annotated[str, PropertyInfo(alias="subjectId")]
    """ID of a subject associated with the event, such as a rollout.

    Combined with other filters using AND.
    """

    types: SequenceNotStr[str]
    """Event types to include, such as `deployment.scaled` or `condition.set`.

    Combined with other filters using AND.
    """

    until: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Return only events strictly before this time."""
