# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EvaluationListParams"]


class EvaluationListParams(TypedDict, total=False):
    limit: int
    """Maximum number of results to return (max 100)"""

    status: Literal["pending", "queued", "running", "completed", "error", "user_error"]
    """Filter by job status"""
