# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["JigRollbackParams"]


class JigRollbackParams(TypedDict, total=False):
    revision_identifier: Required[str]
    """Revision number or revision ID to roll back to."""
