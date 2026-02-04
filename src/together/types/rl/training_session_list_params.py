# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TrainingSessionListParams"]


class TrainingSessionListParams(TypedDict, total=False):
    limit: str
    """Maximum number of sessions to return (1-100)"""

    offset: str
    """Number of sessions to skip"""

    status: str
