# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .endpoint_deployment_summary import EndpointDeploymentSummary
from .endpoint_traffic_split_entry import EndpointTrafficSplitEntry

__all__ = ["Endpoint"]


class Endpoint(BaseModel):
    """
    Stable inference entry point that groups deployments and routes requests among them.
    """

    id: str
    """Unique endpoint identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the endpoint was created."""

    deployments: List[EndpointDeploymentSummary]
    """
    Lightweight summaries of deployments under this endpoint. Retrieve a deployment
    through the endpoint's deployment API for full details.
    """

    endpoint_type: Literal["ENDPOINT_TYPE_DEDICATED", "ENDPOINT_TYPE_SERVERLESS", "ENDPOINT_TYPE_RESERVED"] = FieldInfo(
        alias="endpointType"
    )
    """Serving class of the endpoint. Reserved endpoints use reserved capacity."""

    etag: str
    """
    Opaque version tag for optimistic concurrency control. Supply on update/delete
    to ensure consistent read-modify-write. If not set, the write overwrites based
    on current state.
    """

    name: str
    """
    Project-qualified endpoint name in the form `<project_slug>/<endpoint_name>`.
    Pass this value as `model` in inference requests. Create and update requests may
    use either a bare endpoint name or the qualified form; a supplied project slug
    must match the project in the request path.
    """

    project_id: str = FieldInfo(alias="projectId")
    """ID of the project that owns the endpoint."""

    traffic_split: List[EndpointTrafficSplitEntry] = FieldInfo(alias="trafficSplit")
    """Deployments eligible for live traffic and their capacity weights.

    An empty list leaves the endpoint unrouted.
    """

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Output only. Timestamp when the endpoint was last updated."""

    visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"]
    """Who can discover the endpoint.

    `VISIBILITY_PRIVATE` restricts it to the project; `VISIBILITY_INTERNAL` shares
    it with the organization.
    """

    active_rollout_id: Optional[str] = FieldInfo(alias="activeRolloutId", default=None)
    """ID of the currently active rollout in an in-flight state, including paused."""
