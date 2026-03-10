# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "Deployment",
    "Autoscaling",
    "AutoscalingHTTPAutoscalingConfig",
    "AutoscalingQueueAutoscalingConfig",
    "AutoscalingCustomMetricAutoscalingConfig",
    "EnvironmentVariable",
    "ReplicaEvents",
    "Volume",
]


class AutoscalingHTTPAutoscalingConfig(BaseModel):
    """Autoscaling config for HTTPTotalRequests and HTTPAvgRequestDuration metrics"""

    metric: Optional[Literal["HTTPTotalRequests", "HTTPAvgRequestDuration"]] = None
    """Metric must be HTTPTotalRequests or HTTPAvgRequestDuration"""

    target: Optional[float] = None
    """Target is the threshold value.

    Default: 100 for HTTPTotalRequests, 500 (ms) for HTTPAvgRequestDuration
    """

    time_interval_minutes: Optional[int] = None
    """TimeIntervalMinutes is the rate window in minutes. Default: 10"""


class AutoscalingQueueAutoscalingConfig(BaseModel):
    """Autoscaling config for QueueBacklogPerWorker metric"""

    metric: Optional[Literal["QueueBacklogPerWorker"]] = None
    """Metric must be QueueBacklogPerWorker"""

    model: Optional[str] = None
    """Model overrides the model name for queue status lookup.

    Defaults to the deployment app name
    """

    target: Optional[float] = None
    """Target is the threshold value. Default: 1.01"""


class AutoscalingCustomMetricAutoscalingConfig(BaseModel):
    """Autoscaling config for CustomMetric metric"""

    custom_metric_name: Optional[str] = None
    """CustomMetricName is the Prometheus metric name.

    Required. Must match [a-zA-Z\\__:][a-zA-Z0-9_:]\\**
    """

    metric: Optional[Literal["CustomMetric"]] = None
    """Metric must be CustomMetric"""

    target: Optional[float] = None
    """Target is the threshold value. Default: 500"""


Autoscaling: TypeAlias = Union[
    AutoscalingHTTPAutoscalingConfig, AutoscalingQueueAutoscalingConfig, AutoscalingCustomMetricAutoscalingConfig
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


class ReplicaEvents(BaseModel):
    image: Optional[str] = None
    """Image is the container image used for this replica"""

    replica_ready_since: Optional[str] = None
    """
    ReplicaReadySince is the timestamp when the replica became ready to serve
    traffic
    """

    replica_status: Optional[str] = None
    """
    ReplicaStatus is the current status of the replica (e.g., "Running", "Waiting",
    "Terminated")
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

    revision_id: Optional[str] = None
    """RevisionID is the deployment revision ID associated with this replica"""

    volume_preload_completed_at: Optional[str] = None
    """VolumePreloadCompletedAt is the timestamp when the volume preload completed"""

    volume_preload_started_at: Optional[str] = None
    """VolumePreloadStartedAt is the timestamp when the volume preload started"""

    volume_preload_status: Optional[str] = None
    """
    VolumePreloadStatus is the status of the volume preload (e.g., "InProgress",
    "Completed", "Failed")
    """


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

    version: Optional[int] = None
    """Version is the volume version to mount.

    On create, defaults to the latest version. On update, defaults to the currently
    mounted version.
    """


class Deployment(BaseModel):
    id: Optional[str] = None
    """ID is the unique identifier of the deployment"""

    args: Optional[List[str]] = None
    """Args are the arguments passed to the container's command"""

    autoscaling: Optional[Autoscaling] = None
    """Autoscaling contains autoscaling configuration parameters for this deployment.

    Omitted when autoscaling is disabled (nil)
    """

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

    object: Optional[Literal["deployment"]] = None
    """The object type, which is always `deployment`."""

    port: Optional[int] = None
    """Port is the container port that the deployment exposes"""

    ready_replicas: Optional[int] = None
    """ReadyReplicas is the current number of replicas that are in the Ready state"""

    replica_events: Optional[Dict[str, ReplicaEvents]] = None
    """ReplicaEvents is a mapping of replica names or IDs to their status events"""

    status: Optional[Literal["Updating", "Scaling", "Ready", "Failed", "ScaledToZero"]] = None
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
