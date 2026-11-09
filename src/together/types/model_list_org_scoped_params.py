# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelListOrgScopedParams"]


class ModelListOrgScopedParams(TypedDict, total=False):
    after: str
    """Cursor from a previous list response."""

    limit: int
    """Maximum number of results to return."""

    order_by: Annotated[str, PropertyInfo(alias="orderBy")]
    """Sort field for the results.

    Supports `created_at`, optionally followed by `asc` or `desc`. Defaults to
    ascending.
    """
