# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo
from ..deployment_autoscaling_param import DeploymentAutoscalingParam

__all__ = ["DeploymentUpdateParams"]


class DeploymentUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    update_mask: Annotated[str, PropertyInfo(alias="updateMask")]
    """Fields to update. If not set, the fields populated on `deployment` are updated."""

    autoscaling: DeploymentAutoscalingParam
    """Autoscaling configuration for a deployment."""

    etag: str
    """Current deployment version.

    The update is rejected if this value no longer matches.
    """

    name: str
    """Updated inference-addressable deployment name."""
