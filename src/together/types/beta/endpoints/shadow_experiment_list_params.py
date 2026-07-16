# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ShadowExperimentListParams"]


class ShadowExperimentListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous shadow experiment list response."""

    include_targets: Annotated[bool, PropertyInfo(alias="includeTargets")]
    """Whether to include target deployments in each returned shadow experiment."""

    limit: int
    """Maximum number of shadow experiments to return. Max 500, defaults to 50."""
