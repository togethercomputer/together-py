# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["JigUpdateParams", "EnvironmentVariable", "Volume"]


class JigUpdateParams(TypedDict, total=False):
    args: SequenceNotStr[str]
    """Args overrides the container's CMD.

    Provide as an array of arguments (e.g., ["python", "app.py"])
    """

    autoscaling: Dict[str, str]
    """Autoscaling configuration as key-value pairs.

    Example: {"metric": "QueueBacklogPerWorker", "target": "10"} to scale based on
    queue backlog
    """

    command: SequenceNotStr[str]
    """Command overrides the container's ENTRYPOINT.

    Provide as an array (e.g., ["/bin/sh", "-c"])
    """

    cpu: float
    """
    CPU is the number of CPU cores to allocate per container instance (e.g., 0.1 =
    100 milli cores)
    """

    description: str
    """Description is an optional human-readable description of your deployment"""

    environment_variables: Iterable[EnvironmentVariable]
    """EnvironmentVariables is a list of environment variables to set in the container.

    This will replace all existing environment variables
    """

    gpu_count: int
    """GPUCount is the number of GPUs to allocate per container instance"""

    gpu_type: Literal["h100-80gb", " a100-80gb"]
    """GPUType specifies the GPU hardware to use (e.g., "h100-80gb")"""

    health_check_path: str
    """HealthCheckPath is the HTTP path for health checks (e.g., "/health").

    Set to empty string to disable health checks
    """

    image: str
    """Image is the container image to deploy from registry.together.ai."""

    max_replicas: int
    """MaxReplicas is the maximum number of replicas that can be scaled up to."""

    memory: float
    """
    Memory is the amount of RAM to allocate per container instance in GiB (e.g., 0.5
    = 512MiB)
    """

    min_replicas: int
    """MinReplicas is the minimum number of replicas to run"""

    name: str
    """Name is the new unique identifier for your deployment.

    Must contain only alphanumeric characters, underscores, or hyphens (1-100
    characters)
    """

    port: int
    """
    Port is the container port your application listens on (e.g., 8080 for web
    servers)
    """

    storage: int
    """
    Storage is the amount of ephemeral disk storage to allocate per container
    instance (e.g., 10 = 10GiB)
    """

    termination_grace_period_seconds: int
    """
    TerminationGracePeriodSeconds is the time in seconds to wait for graceful
    shutdown before forcefully terminating the replica
    """

    volumes: Iterable[Volume]
    """Volumes is a list of volume mounts to attach to the container.

    This will replace all existing volumes
    """


class EnvironmentVariable(TypedDict, total=False):
    name: Required[str]
    """Name is the environment variable name (e.g., "DATABASE_URL").

    Must start with a letter or underscore, followed by letters, numbers, or
    underscores
    """

    value: str
    """Value is the plain text value for the environment variable.

    Use this for non-sensitive values. Either Value or ValueFromSecret must be set,
    but not both
    """

    value_from_secret: str
    """ValueFromSecret references a secret by name or ID to use as the value.

    Use this for sensitive values like API keys or passwords. Either Value or
    ValueFromSecret must be set, but not both
    """


class Volume(TypedDict, total=False):
    mount_path: Required[str]
    """
    MountPath is the path in the container where the volume will be mounted (e.g.,
    "/data")
    """

    name: Required[str]
    """Name is the name of the volume to mount.

    Must reference an existing volume by name or ID
    """
