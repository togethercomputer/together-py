# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["ShadowExperimentTarget"]


class ShadowExperimentTarget(BaseModel):
    """Deployment that receives mirrored traffic for a shadow experiment."""

    id: str
    """Output only. Unique shadow experiment target identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Output only. Timestamp when the target was created."""

    etag: str
    """Opaque version tag for optimistic concurrency control.

    Returned on read; set it on update or delete requests for consistent
    read-modify-write.
    """

    experiment_id: str = FieldInfo(alias="experimentId")
    """Output only. Shadow experiment this target belongs to."""

    name: str
    """Human-readable target name, unique within the shadow experiment.

    At most 256 characters.
    """

    target_deployment_id: str = FieldInfo(alias="targetDeploymentId")
    """Deployment under the parent endpoint that receives mirrored traffic.

    Shadow targets should be excluded from the endpoint's live traffic split.
    """

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Output only. Timestamp when the target was last updated."""

    description: Optional[str] = None
    """Optional free-form target description."""
