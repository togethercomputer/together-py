# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AdapterUpdateParams"]


class AdapterUpdateParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    endpoint_id: Required[Annotated[str, PropertyInfo(alias="endpointId")]]
    """Endpoint identifier."""

    deployment_id: Required[Annotated[str, PropertyInfo(alias="deploymentId")]]
    """Deployment identifier."""

    adapter_revision_id: Required[Annotated[str, PropertyInfo(alias="adapterRevisionId")]]
    """New adapter revision to pin."""

    etag: Required[str]
    """
    Row-level etag from a prior AddAdapter, UpdateAdapter, GetAdapter, or
    ListAdapters response.
    """
