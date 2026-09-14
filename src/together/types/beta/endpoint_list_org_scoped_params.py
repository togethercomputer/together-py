# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["EndpointListOrgScopedParams"]


class EndpointListOrgScopedParams(TypedDict, total=False):
    after: str
    """Cursor from a previous list response."""

    filter: str
    """
    Filter expression using `name`, `created_at`, or `updated_at` with comparison
    operators and AND/OR/NOT; timestamps must be RFC 3339 strings. `name` supports
    substring matching with `:` and prefix/suffix wildcards with `*`, and must be a
    bare endpoint name.
    """

    limit: int
    """Maximum number of results to return."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Sort field for the results.

    Supports `created_at` or `updated_at`, optionally followed by `asc` or `desc`.
    """
