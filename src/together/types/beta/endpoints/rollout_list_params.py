# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["RolloutListParams"]


class RolloutListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous rollout list response."""

    filter: Literal["ROLLOUT_FILTER_ACTIVE", "ROLLOUT_FILTER_TERMINAL"]
    """Narrow results to active or terminal rollouts. Omit to list all rollouts."""

    limit: int
    """Maximum number of rollouts to return. Max 500, defaults to 50."""
