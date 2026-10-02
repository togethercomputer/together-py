# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["JigListRevisionsParams"]


class JigListRevisionsParams(TypedDict, total=False):
    before: int
    """
    Return only events with event_number strictly less than this value for
    pagination.
    """

    limit: int
    """Maximum number of events to return (default 10, max 100)."""
