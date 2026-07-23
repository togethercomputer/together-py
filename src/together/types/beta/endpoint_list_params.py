# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EndpointListParams"]


class EndpointListParams(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project identifier."""

    after: str
    """Cursor from a previous response."""

    filter: str
    """
    Filter expression using `name`, `created_at`, or `updated_at` with comparison
    operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
    substring matching with `:` and prefix/suffix wildcards with `*`, and accepts a
    bare endpoint name or `<project_slug>/<endpoint_name>`.
    """

    limit: int
    """Maximum number of endpoints to return."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Sort field for the results.

    Supports `created_at` or `updated_at`, optionally followed by `asc` or `desc`.
    """
