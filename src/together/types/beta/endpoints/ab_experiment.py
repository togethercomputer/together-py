# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..ab_member import AbMember

__all__ = ["AbExperiment"]


class AbExperiment(BaseModel):
    """
    Managed cohort split that subdivides a control deployment's live traffic among the control and one or more variants.
    """

    id: str
    """Output only. Unique A/B experiment identifier."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Output only. Timestamp when the A/B experiment was created."""

    created_by: str = FieldInfo(alias="createdBy")
    """Output only. Identifier of the principal that created the A/B experiment."""

    endpoint_id: str = FieldInfo(alias="endpointId")
    """Output only. Endpoint this A/B experiment belongs to."""

    etag: str
    """Optional opaque version tag for optimistic concurrency control."""

    members: List[AbMember]
    """
    Two to 20 participating deployments with exactly one control and percentages
    that add up to 100.
    """

    name: str
    """Human-readable A/B experiment name, unique within the endpoint."""

    project_id: str = FieldInfo(alias="projectId")
    """Output only. Project that owns the parent endpoint."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Output only. Timestamp when the A/B experiment was last updated."""

    description: Optional[str] = None
    """Optional free-form description."""
