# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EvalUpdateParams"]


class EvalUpdateParams(TypedDict, total=False):
    error: str
    """Error message when status is 'error' or 'user_error'"""

    results: object
    """The results of the evaluation job.

    The concrete structure depends on the type of evaluation job
    """

    status: Literal["completed", "error", "user_error", "running", "queued", "pending"]
