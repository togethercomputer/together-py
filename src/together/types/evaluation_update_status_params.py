# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["EvaluationUpdateStatusParams"]


class EvaluationUpdateStatusParams(TypedDict, total=False):
    status: Required[Literal["completed", "error", "running", "queued", "user_error", "inference_error"]]
    """The new status for the job"""

    error: str
    """Error message"""

    results: object
    """Job results (required when status is 'completed')"""
