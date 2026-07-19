# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["TargetCreateParams"]


class TargetCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    experiment_id: Required[Annotated[str, PropertyInfo(alias="experimentId")]]
    """Shadow experiment identifier."""

    name: Required[str]
    """Human-readable target name, unique within the shadow experiment.

    At most 256 characters.
    """

    target_deployment_id: Required[Annotated[str, PropertyInfo(alias="targetDeploymentId")]]
    """Deployment under the parent endpoint that receives mirrored traffic.

    Exclude it from the endpoint's live traffic split.
    """

    description: str
    """Optional free-form target description."""
