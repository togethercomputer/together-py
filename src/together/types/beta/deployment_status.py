# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DeploymentStatus", "Details", "DetailsRegion"]


class DetailsRegion(BaseModel):
    """Realized scheduled and ready replica counts for one deployment region."""

    ready_replicas: int = FieldInfo(alias="readyReplicas")
    """Replicas serving traffic in this region."""

    region: str
    """Region name using the same vocabulary accepted by inline placement regions."""

    scheduled_replicas: int = FieldInfo(alias="scheduledReplicas")
    """Replicas the scheduler has placed in this region."""


class Details(BaseModel):
    """Deployment status broken down by each supported dimension."""

    region: List[DetailsRegion]
    """
    Regions where the deployment is actually scheduled or serving replicas, sorted
    by region.
    """


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

    details: Optional[Details] = None
    """Deployment status broken down by each supported dimension."""

    ready_replicas: Optional[int] = FieldInfo(alias="readyReplicas", default=None)
    """Total replicas actively serving traffic across all clusters."""

    scheduled_replicas: Optional[int] = FieldInfo(alias="scheduledReplicas", default=None)
    """Replicas the scheduler has placed on clusters."""
