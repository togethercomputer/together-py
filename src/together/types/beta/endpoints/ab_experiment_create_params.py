# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..ab_member_param import AbMemberParam

__all__ = ["AbExperimentCreateParams"]


class AbExperimentCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    members: Required[Iterable[AbMemberParam]]
    """Two to 20 participating deployments with exactly one control.

    Integer traffic percentages across all members must add up to 100.
    """

    name: Required[str]
    """Human-readable A/B experiment name, unique within the endpoint."""

    description: str
    """Optional free-form description."""
