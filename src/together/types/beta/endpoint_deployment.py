# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .deployment_status import DeploymentStatus
from .deployment_autoscaling import DeploymentAutoscaling
from .deployment_placement_config import DeploymentPlacementConfig

__all__ = ["EndpointDeployment", "Autoscaling", "Placement", "PlacementInline", "PlacementProfile", "RuntimeInfo"]


class Autoscaling(DeploymentAutoscaling):
    """Replica bounds, timing windows, and metrics that control horizontal scaling."""

    pass


class PlacementInline(BaseModel):
    inline: DeploymentPlacementConfig
    """Inline placement parameters expanded into scheduling rules by the server."""


class PlacementProfile(BaseModel):
    profile: str
    """UID of a saved placement profile."""


Placement: TypeAlias = Union[PlacementInline, PlacementProfile]


class RuntimeInfo(BaseModel):
    """Runtime information derived from the deployment's configuration."""

    engine_type: Optional[str] = FieldInfo(alias="engineType", default=None)
    """Serving engine, such as `vllm`, `trtllm`, or `sglang`."""

    engine_version: Optional[str] = FieldInfo(alias="engineVersion", default=None)
    """Version of the serving engine."""

    function_calling_supported: Optional[bool] = FieldInfo(alias="functionCallingSupported", default=None)
    """Whether the runtime accepts tool and function-calling requests."""

    structured_output_supported: Optional[bool] = FieldInfo(alias="structuredOutputSupported", default=None)
    """Whether the runtime can constrain generation to a structured output schema."""


class EndpointDeployment(BaseModel):
    """
    Serving workload that binds a model and immutable config to an endpoint and manages its replicas.
    """

    id: str
    """Unique deployment identifier."""

    autoscaling: Autoscaling
    """Replica bounds, timing windows, and metrics that control horizontal scaling."""

    config: str
    """
    Immutable config revision in the form
    `projects/{projectId}/configs/{configRevisionId}`.
    """

    config_id: str = FieldInfo(alias="configId")
    """Deprecated.

    Use `config`. Config revision identifier, populated during migration.
    """

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the deployment was created."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """ID of the endpoint that contains the deployment."""

    etag: str
    """Opaque version tag for optimistic concurrency control.

    Supply on update/delete to ensure consistent read-modify-write. If not set, the
    write overwrites based on current state.
    """

    hardware: str
    """Hardware selected by the deployment config, including GPU type and count."""

    model: str
    """
    Pinned model resource in the form
    `projects/{projectId}/models/{modelId}/revisions/{revisionId}`.
    """

    api_model_id: str = FieldInfo(alias="modelId")
    """Deprecated.

    Use `model`. Model identifier being served, populated during migration.
    """

    api_model_revision_id: str = FieldInfo(alias="modelRevisionId")
    """Deprecated.

    Use `model` with a /revisions/{revisionId} segment. Pin to a specific model
    revision.
    """

    name: str
    """
    Project- and endpoint-qualified deployment name in the form
    `<project_slug>/<endpoint_name>/<deployment_name>`. Pass it as `model` in an
    inference request to target this deployment directly instead of using the
    endpoint's traffic split.
    """

    project_id: str = FieldInfo(alias="projectId")
    """ID of the project that owns the deployment."""

    status: DeploymentStatus
    """Current status of a deployment, derived at read time from internal state."""

    traffic_mode: Literal["TRAFFIC_MODE_LIVE", "TRAFFIC_MODE_SHADOW"] = FieldInfo(alias="trafficMode")
    """
    Whether the deployment serves client-visible responses or only mirrored shadow
    traffic.
    """

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Timestamp when the deployment was last updated."""

    desired_replicas: Optional[int] = FieldInfo(alias="desiredReplicas", default=None)
    """Number of replicas the autoscaler currently wants across all regions."""

    enable_lora: Optional[bool] = FieldInfo(alias="enableLora", default=None)
    """Whether the deployment can dynamically load LoRA adapters."""

    estimated_effective_traffic_share: Optional[float] = FieldInfo(alias="estimatedEffectiveTrafficShare", default=None)
    """
    Estimated fraction in [0, 1] of endpoint traffic that reaches this deployment
    under the current routing configuration. Absent or unrouted deployments are 0.
    """

    placement: Optional[Placement] = None
    """Placement controls where a deployment is scheduled."""

    runtime_info: Optional[RuntimeInfo] = FieldInfo(alias="runtimeInfo", default=None)
    """Runtime information derived from the deployment's configuration."""

    speculator: Optional[str] = None
    """
    Pinned draft-model resource used for speculative decoding, in the same form as
    `model`. Omitted when speculative decoding is disabled.
    """

    speculator_id: Optional[str] = FieldInfo(alias="speculatorId", default=None)
    """Deprecated.

    Use `speculator`. Speculative decoding model identifier derived from the
    deployment config.
    """

    speculator_revision_id: Optional[str] = FieldInfo(alias="speculatorRevisionId", default=None)
    """Deprecated.

    Use `speculator`. ID of the speculative decoding draft-model revision pinned at
    creation time.
    """
