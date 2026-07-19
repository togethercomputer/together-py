# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DeploymentStatus"]


class DeploymentStatus(BaseModel):
    """Current status of a deployment, derived at read time from internal state."""

    message: str
    """Human-readable explanation of the current state."""

    state: Literal[
        "DEPLOYMENT_STATE_PROVISIONING",
        "DEPLOYMENT_STATE_READY",
        "DEPLOYMENT_STATE_SCALING",
        "DEPLOYMENT_STATE_DEGRADED",
        "DEPLOYMENT_STATE_FAILED",
        "DEPLOYMENT_STATE_STOPPED",
        "DEPLOYMENT_STATE_STOPPING",
    ]
    """High-level lifecycle state."""

    ready_replicas: Optional[int] = FieldInfo(alias="readyReplicas", default=None)
    """Total replicas actively serving traffic across all clusters."""

    scheduled_replicas: Optional[int] = FieldInfo(alias="scheduledReplicas", default=None)
    """Replicas the scheduler has placed on clusters."""
