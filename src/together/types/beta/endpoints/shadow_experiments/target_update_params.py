# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["TargetUpdateParams"]


class TargetUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    experiment_id: Required[Annotated[str, PropertyInfo(alias="experimentId")]]
    """Shadow experiment identifier."""

    update_mask: Required[Annotated[str, PropertyInfo(alias="updateMask")]]
    """Comma-separated fields to update.

    Supported fields are `name`, `targetDeploymentId`, and `description`.
    """

    description: str
    """Updated free-form target description."""

    etag: str
    """Opaque version tag from a prior read for optimistic concurrency."""

    name: str
    """Updated human-readable target name."""

    target_deployment_id: Annotated[str, PropertyInfo(alias="targetDeploymentId")]
    """Replacement deployment under the parent endpoint.

    Exclude it from the endpoint's live traffic split.
    """
