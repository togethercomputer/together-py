# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AbMember"]


class AbMember(BaseModel):
    """Deployment participating in an A/B experiment."""

    deployment_id: str = FieldInfo(alias="deploymentId")
    """Deployment under the parent endpoint."""

    percent: int
    """Integer traffic percent in [1, 100].

    Percentages across all members must sum to 100.
    """

    role: Literal["AB_EXPERIMENT_MEMBER_ROLE_CONTROL", "AB_EXPERIMENT_MEMBER_ROLE_VARIANT"]
    """Role of this deployment within the A/B experiment."""
