# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = [
    "Deployment",
    "EnvironmentVariable",
    "ReplicaEvents",
    "ReplicaEventsContainerStatus",
    "ReplicaEventsEvent",
    "Volume",
]


class EnvironmentVariable(BaseModel):
    name: str
    """Name is the environment variable name (e.g., "DATABASE_URL").

    Must start with a letter or underscore, followed by letters, numbers, or
    underscores
    """

    value: Optional[str] = None
    """Value is the plain text value for the environment variable.

    Use this for non-sensitive values. Either Value or ValueFromSecret must be set,
    but not both
    """

    value_from_secret: Optional[str] = None
    """ValueFromSecret references a secret by name or ID to use as the value.

    Use this for sensitive values like API keys or passwords. Either Value or
    ValueFromSecret must be set, but not both
    """


class ReplicaEventsContainerStatus(BaseModel):
    """
    ContainerStatus provides detailed status information about the container within this replica
    """

    finished_at: Optional[str] = FieldInfo(alias="finishedAt", default=None)
    """
    FinishedAt is the timestamp when the container finished execution (if
    terminated)
    """

    message: Optional[str] = None
    """
    Message provides a human-readable message with details about the container's
    status
    """

    name: Optional[str] = None
    """Name is the name of the container"""

    reason: Optional[str] = None
    """
    Reason provides a brief machine-readable reason for the container's current
    status
    """

    started_at: Optional[str] = FieldInfo(alias="startedAt", default=None)
    """StartedAt is the timestamp when the container started execution"""

    status: Optional[str] = None
    """
    Status is the current state of the container (e.g., "Running", "Terminated",
    "Waiting")
    """


class ReplicaEventsEvent(BaseModel):
    action: Optional[str] = None
    """Action is the action taken or reported by this event"""

    count: Optional[int] = None
    """Count is the number of times this event has occurred"""

    first_seen: Optional[str] = None
    """FirstSeen is the timestamp when this event was first observed"""

    last_seen: Optional[str] = None
    """LastSeen is the timestamp when this event was last observed"""

    message: Optional[str] = None
    """Message is a human-readable description of the event"""

    reason: Optional[str] = None
    """
    Reason is a brief machine-readable reason for this event (e.g., "Pulling",
    "Started", "Failed")
    """


class ReplicaEvents(BaseModel):
    container_status: Optional[ReplicaEventsContainerStatus] = None
    """
    ContainerStatus provides detailed status information about the container within
    this replica
    """

    events: Optional[List[ReplicaEventsEvent]] = None
    """
    Events is a list of Kubernetes events related to this replica for
    troubleshooting
    """

    replica_completed_at: Optional[str] = None
    """ReplicaCompletedAt is the timestamp when the replica finished execution"""

    replica_marked_for_termination_at: Optional[str] = None
    """
    ReplicaMarkedForTerminationAt is the timestamp when the replica was marked for
    termination
    """

    replica_ready_since: Optional[str] = None
    """
    ReplicaReadySince is the timestamp when the replica became ready to serve
    traffic
    """

    replica_running_since: Optional[str] = None
    """ReplicaRunningSince is the timestamp when the replica entered the running state"""

    replica_started_at: Optional[str] = None
    """ReplicaStartedAt is the timestamp when the replica was created"""

    replica_status: Optional[str] = None
    """
    ReplicaStatus is the current status of the replica (e.g., "Running", "Pending",
    "Failed")
    """

    replica_status_message: Optional[str] = None
    """
    ReplicaStatusMessage provides a human-readable message explaining the replica's
    status
    """

    replica_status_reason: Optional[str] = None
    """
    ReplicaStatusReason provides a brief machine-readable reason for the replica's
    status
    """

    scheduled_on_cluster: Optional[str] = None
    """ScheduledOnCluster identifies which cluster this replica is scheduled on"""


class Volume(BaseModel):
    mount_path: str
    """
    MountPath is the path in the container where the volume will be mounted (e.g.,
    "/data")
    """

    name: str
    """Name is the name of the volume to mount.

    Must reference an existing volume by name or ID
    """


class Deployment(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier of the deployment"""

    args: Optional[List[str]] = None
    """Args are the arguments passed to the container's command"""

    autoscaling: Optional[Dict[str, str]] = None
    """Autoscaling contains autoscaling configuration parameters for this deployment"""

    command: Optional[List[str]] = None
    """Command is the entrypoint command run in the container"""

    cpu: Optional[float] = None
    """
    CPU is the amount of CPU resource allocated to each replica in cores (fractional
    value is allowed)
    """

    created_at: Optional[str] = None
    """CreatedAt is the ISO8601 timestamp when this deployment was created"""

    description: Optional[str] = None
    """
    Description provides a human-readable explanation of the deployment's purpose or
    content
    """

    desired_replicas: Optional[int] = None
    """DesiredReplicas is the number of replicas that the orchestrator is targeting"""

    environment_variables: Optional[List[EnvironmentVariable]] = None
    """EnvironmentVariables is a list of environment variables set in the container"""

    gpu_count: Optional[int] = None
    """GPUCount is the number of GPUs allocated to each replica in this deployment"""

    gpu_type: Optional[Literal["h100-80gb", " a100-80gb"]] = None
    """GPUType specifies the type of GPU requested (if any) for this deployment"""

    health_check_path: Optional[str] = None
    """HealthCheckPath is the HTTP path used for health checks of the application"""

    image: Optional[str] = None
    """Image specifies the container image used for this deployment"""

    max_replicas: Optional[int] = None
    """MaxReplicas is the maximum number of replicas to run for this deployment"""

    memory: Optional[float] = None
    """
    Memory is the amount of memory allocated to each replica in GiB (fractional
    value is allowed)
    """

    min_replicas: Optional[int] = None
    """MinReplicas is the minimum number of replicas to run for this deployment"""

    name: Optional[str] = None
    """Name is the name of the deployment"""

    object: Optional[str] = None
    """Object is the type identifier for this response (always "deployment")"""

    port: Optional[int] = None
    """Port is the container port that the deployment exposes"""

    ready_replicas: Optional[int] = None
    """ReadyReplicas is the current number of replicas that are in the Ready state"""

    replica_events: Optional[Dict[str, ReplicaEvents]] = None
    """ReplicaEvents is a mapping of replica names or IDs to their status events"""

    status: Optional[Literal["Updating", "Scaling", "Ready", "Failed"]] = None
    """
    Status represents the overall status of the deployment (e.g., Updating, Scaling,
    Ready, Failed)
    """

    storage: Optional[int] = None
    """
    Storage is the amount of storage (in MB or units as defined by the platform)
    allocated to each replica
    """

    updated_at: Optional[str] = None
    """UpdatedAt is the ISO8601 timestamp when this deployment was last updated"""

    volumes: Optional[List[Volume]] = None
    """Volumes is a list of volume mounts for this deployment"""
