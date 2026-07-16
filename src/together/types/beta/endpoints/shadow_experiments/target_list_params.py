# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["TargetListParams"]


class TargetListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous shadow experiment target list response."""

    limit: int
    """Maximum number of targets to return. Max 500, defaults to 50."""
