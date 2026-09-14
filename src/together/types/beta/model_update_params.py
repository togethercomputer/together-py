# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ModelUpdateParams"]


class ModelUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """Fields to update. If omitted, all mutable fields are overwritten."""

    description: str
    """Updated user-facing model description."""

    name: str
    """Updated inference-addressable model name."""

    visibility: Literal["VISIBILITY_PRIVATE", "VISIBILITY_INTERNAL"]
    """Who can discover the model.

    `VISIBILITY_PRIVATE` restricts it to the project; `VISIBILITY_INTERNAL` shares
    it with the organization.
    """
