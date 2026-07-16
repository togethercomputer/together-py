# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AdapterCreateParams"]


class AdapterCreateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """Deployment identifier."""

    adapter_model_id: Required[Annotated[str, PropertyInfo(alias="adapterModelId")]]
    """Adapter model identifier to attach."""

    adapter_revision_id: Annotated[str, PropertyInfo(alias="adapterRevisionId")]
    """Optional adapter revision to pin.

    If omitted, the latest revision is resolved at request time.
    """

    force: bool
    """Whether to evict the oldest adapter if the deployment is at adapter capacity."""
