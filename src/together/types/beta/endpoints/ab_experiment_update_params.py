# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..ab_member_param import AbMemberParam

__all__ = ["AbExperimentUpdateParams"]


class AbExperimentUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """Fields to update. If omitted, all mutable fields are overwritten."""

    description: str
    """Updated free-form description."""

    etag: str
    """Opaque version tag from a prior read for optimistic concurrency."""

    members: Iterable[AbMemberParam]
    """Complete replacement member set.

    Requires two to 20 deployments, exactly one control, and percentages that add up
    to 100.
    """
