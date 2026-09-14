# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["EvalListParams"]


class EvalListParams(TypedDict, total=False):
    limit: int
    """Limit the number of results"""

    status: str
    """Filter evaluation jobs by status"""
