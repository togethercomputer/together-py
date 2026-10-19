# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["CostListParams"]


class CostListParams(TypedDict, total=False):
    after: str
    """Opaque cursor from a previous response's `next_cursor`.

    Only valid for the month and granularity it was issued for. Current-month data
    is a moving snapshot: each page reflects data as of its request, so newly
    completed windows may appear at the end of the sequence.
    """

    granularity: Literal["day", "hour"]
    """Time window size for rows. 'hour' returns ~24x more rows than 'day'."""

    limit: int
    """Maximum number of time windows per page (max 1000)."""

    month: str
    """Billing month in YYYY-MM format.

    Defaults to the current month, which returns data through yesterday (daily) or
    the last completed hour (hourly).
    """

    organization_id: str
    """Organization to report on.

    Usage is always reported for the organization that owns the API key, so this is
    optional; supplying an ID that is not that organization returns 403.
    """
