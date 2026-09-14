# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AbMemberParam"]


class AbMemberParam(TypedDict, total=False):
    """Deployment participating in an A/B experiment."""

    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """Deployment under the parent endpoint."""

    percent: Required[int]
    """Integer traffic percent in [1, 100].

    Percentages across all members must sum to 100.
    """

    role: Required[Literal["AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "AB_EXPERIMENT_MEMBER_ROLE_VARIANT"]]
    """Role of this deployment within the A/B experiment."""
