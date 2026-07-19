# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .deployment_autoscaling import DeploymentAutoscaling

__all__ = ["EndpointDeploymentSummary", "Autoscaling"]


class Autoscaling(DeploymentAutoscaling):
    """Autoscaling configuration for the deployment."""

    pass


class EndpointDeploymentSummary(BaseModel):
    """Compact deployment status embedded in an endpoint response."""

    id: str
    """Deployment identifier."""

    autoscaling: Autoscaling
    """Autoscaling configuration for the deployment."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Timestamp when the deployment was created."""

    hardware: str
    """
    Hardware configuration selected by the deployment's config, such as its GPU type
    and count.
    """

    model: str
    """
    Resource name of the served model in the form
    `projects/{projectId}/models/{modelId}/revisions/{revisionId}`. For public
    models, the model's owning project may differ from the deployment's project.
    """

    api_model_id: str = FieldInfo(alias="modelId")
    """Deprecated. Use `model`. Model identifier being served."""

    name: str
    """
    Inference-addressable name in the fully-qualified form
    "<project_slug>/<endpoint_name>/<deployment_name>". Pass it as the "model" field
    when calling the inference API to pin to this deployment.
    """

    state: Literal[
        "DEPLOYMENT_STATE_PROVISIONING",
        "DEPLOYMENT_STATE_READY",
        "DEPLOYMENT_STATE_SCALING",
        "DEPLOYMENT_STATE_DEGRADED",
        "DEPLOYMENT_STATE_FAILED",
        "DEPLOYMENT_STATE_STOPPED",
        "DEPLOYMENT_STATE_STOPPING",
    ]
    """Current state of the deployment."""

    traffic_mode: Literal["TRAFFIC_MODE_LIVE", "TRAFFIC_MODE_SHADOW"] = FieldInfo(alias="trafficMode")
    """
    Whether the deployment serves client-visible responses or only mirrored shadow
    traffic.
    """

    desired_replicas: Optional[int] = FieldInfo(alias="desiredReplicas", default=None)
    """Number of replicas the autoscaler currently wants across all regions."""

    estimated_effective_traffic_share: Optional[float] = FieldInfo(alias="estimatedEffectiveTrafficShare", default=None)
    """
    Estimated fraction from 0 to 1 of endpoint traffic currently routed to this
    deployment.
    """

    ready_replicas: Optional[int] = FieldInfo(alias="readyReplicas", default=None)
    """Number of replicas currently ready to serve requests across all regions."""
