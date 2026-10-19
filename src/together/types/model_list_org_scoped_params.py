# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ModelListOrgScopedParams"]


class ModelListOrgScopedParams(TypedDict, total=False):
    after: str
    """Cursor from a previous list response."""

    limit: int
    """Maximum number of results to return."""
