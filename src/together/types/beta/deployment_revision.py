# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "DeploymentRevision",
    "EnvironmentVariable",
    "Volume",
    "Autoscaling",
    "AutoscalingHTTPAutoscalingConfig",
    "AutoscalingQueueAutoscalingConfig",
    "AutoscalingCustomMetricAutoscalingConfig",
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


class Volume(BaseModel):
    mount_path: str
    """MountPath is the path in the container where the volume mounts (e.g., "/data")."""

    name: str
    """Name is the name of the volume to mount.

    Must reference an existing volume by name or ID
    """

    version: Optional[int] = None
    """Version is the volume version to mount.

    On create, defaults to the latest version. On update, defaults to the currently
    mounted version.
    """


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

    Must match [a-zA-Z\\__:][a-zA-Z0-9_:]\\**
    """

    metric: Optional[Literal["CustomMetric"]] = None
    """Metric must be CustomMetric"""

    target: Optional[float] = None
    """Target is the threshold value. Default: 500"""


Autoscaling: TypeAlias = Union[
    AutoscalingHTTPAutoscalingConfig, AutoscalingQueueAutoscalingConfig, AutoscalingCustomMetricAutoscalingConfig
]


class DeploymentRevision(BaseModel):
    """Deployment configuration captured for one retained revision."""

    args: List[str]
    """Arguments passed to the container command."""

    capacity_type: Literal["stable", "preemptible"]
    """Capacity behavior for replicas above reserved capacity."""

    command: List[str]
    """Entrypoint command run by the container."""

    cpu: float
    """CPU cores allocated to each replica."""

    created_at: datetime
    """Time when this revision was created."""

    environment_variables: List[EnvironmentVariable]
    """Environment variables configured on this revision."""

    gpu_count: int
    """Number of GPUs allocated to each replica."""

    gpu_type: str
    """GPU hardware type configured for this revision."""

    health_check_path: str
    """HTTP path used for health checks."""

    image: str
    """Container image used by this revision."""

    max_replicas: int
    """Maximum number of replicas configured for this revision."""

    memory: float
    """Memory allocated to each replica in GiB."""

    min_replicas: int
    """Minimum number of replicas configured for this revision."""

    object: Literal["revision"]
    """The object type, which is always `revision`."""

    port: int
    """Container port exposed by this revision."""

    protocol: str
    """Network protocol served by the deployment revision."""

    revision_id: str
    """Unique revision identifier."""

    storage: int
    """Ephemeral storage allocated to each replica."""

    volumes: List[Volume]
    """Volume mounts attached to this revision."""

    autoscaling: Optional[Autoscaling] = None
    """Autoscaling configuration captured for this revision."""

    termination_grace_period_seconds: Optional[int] = None
    """Seconds to wait for graceful shutdown before forcefully terminating a replica."""
