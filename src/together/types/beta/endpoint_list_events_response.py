# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["EndpointListEventsResponse"]


class EndpointListEventsResponse(BaseModel):
    """
    One endpoint- or deployment-scoped entry in an endpoint's combined audit and lifecycle feed.
    """

    id: str
    """Output only. Unique event identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Output only. Event creation time."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. The endpoint this event belongs to. Always set."""

    level: Literal["LEVEL_DEBUG", "LEVEL_INFO", "LEVEL_WARN", "LEVEL_ERROR"]
    """Output only. Severity level."""

    source: str
    """Output only. Service, cluster, or controller that emitted the event."""

    source_kind: Literal["SOURCE_KIND_ENDPOINT", "SOURCE_KIND_DEPLOYMENT"] = FieldInfo(alias="sourceKind")
    """Output only. Whether this row describes the endpoint or one of its deployments."""

    type: str
    """Output only.

    Stable event type, such as `endpoint.updated`, `deployment.created`,
    `deployment.scaled`, `condition.set`, or `pod.log`.
    """

    cluster_id: Optional[str] = FieldInfo(alias="clusterId", default=None)
    """ID of the cluster associated with a cluster-scoped event."""

    container_name: Optional[str] = FieldInfo(alias="containerName", default=None)
    """
    Stable public component label associated with a replica event, such as `engine`,
    `model-download`, or `sidecar`.
    """

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """Output only.

    Deployment associated with the event when `sourceKind` is
    `SOURCE_KIND_DEPLOYMENT`.
    """

    log_excerpt: Optional[str] = FieldInfo(alias="logExcerpt", default=None)
    """
    Short diagnostic log excerpt captured with a pod event, for example during a
    crash, out-of-memory termination, or image pull failure. This field is truncated
    and is not a streaming log API.
    """

    message: Optional[str] = None
    """Output only.

    Human-readable description of the event. Short and stable; not structured data.
    """

    name: Optional[str] = None
    """Resource name at the time of the event.

    Populated by: deployment.created, deployment.deleted, endpoint.created,
    endpoint.deleted
    """

    new_replicas: Optional[int] = FieldInfo(alias="newReplicas", default=None)
    """New replica count for a `deployment.scaled` event."""

    node_id: Optional[str] = FieldInfo(alias="nodeId", default=None)
    """Opaque node handle for correlating replica failures on the same node.

    Omitted when the replica is unscheduled or the node is unknown.
    """

    old_replicas: Optional[int] = FieldInfo(alias="oldReplicas", default=None)
    """Replica-count transition. Populated by: deployment.scaled"""

    paths: Optional[List[str]] = None
    """Field-mask paths that were modified.

    Populated by: deployment.updated, endpoint.updated
    """

    reason: Optional[str] = None
    """
    Stable condition reason, such as `AllReplicasReady`, `ReplicasProgressing`, or
    `ApplySuccessful`.
    """

    replica_id: Optional[str] = FieldInfo(alias="replicaId", default=None)
    """
    Opaque replica identity associated with a `pod.*` event, stable for grouping
    events from the same replica.
    """

    service_type: Optional[str] = FieldInfo(alias="serviceType", default=None)
    """
    Deployment subservice associated with the event, such as `model-deployment` or
    `speculator-deployment`.
    """

    status: Optional[str] = None
    """
    Condition status for `condition.set` and `cluster_condition.set`: `True`,
    `False`, or `Unknown`. The condition type is carried in `subjectId`.
    """

    subject_id: Optional[str] = FieldInfo(alias="subjectId", default=None)
    """Output only.

    ID of the event's subject, such as a rollout, shadow target, or condition type.
    """

    version: Optional[int] = None
    """Target version.

    Populated by `target.created`; the target ID is carried in `subjectId`.
    """
