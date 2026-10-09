# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AdapterDeleteParams"]


class AdapterDeleteParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """Deployment identifier."""

    etag: Required[str]
    """Adapter etag from a previous add, update, get, or list response.

    The removal is rejected if the adapter changed after that response.
    """

    adapter_model_id: Annotated[str, PropertyInfo(alias="adapterModelId")]
    """Deprecated optional cross-check.

    When set, this must equal the `ml_` id of the adapter model pinned by the live
    attachment; model names are not accepted.
    """
