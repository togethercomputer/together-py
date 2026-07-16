# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DeploymentListParams"]


class DeploymentListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """ID of the project that owns the endpoint."""

    after: str
    """Cursor from a previous deployment list response."""

    filter: str
    """
    Filter expression using `name`, `state`, `model`, `created_at`, or `updated_at`
    with comparison operators and AND/OR/NOT; `state` takes a DeploymentState enum
    name and `model` takes a model resource name. `name` supports substring matching
    with `:` and prefix/suffix wildcards with `*`, and accepts a bare deployment
    name or `<project_slug>/<endpoint_name>/<deployment_name>`.
    """

    limit: int
    """Maximum number of deployments to return. Max 500, defaults to 50."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Sort field for the results.

    Supports `created_at` or `updated_at`, optionally followed by `asc` or `desc`.
    """
