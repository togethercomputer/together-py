# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PlacementProfile"]


class PlacementProfile(BaseModel):
    """Reusable ordered region preferences for scheduling a project's deployments."""

    id: str
    """Unique placement profile identifier."""

    name: str
    """Human-readable placement profile name."""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization that owns the placement profile."""

    preferred_regions: List[str] = FieldInfo(alias="preferredRegions")
    """Preferred deployment regions in descending priority order."""

    project_id: str = FieldInfo(alias="projectId")
    """Project that owns the placement profile."""
