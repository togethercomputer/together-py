# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["CheckpointListParams"]


class CheckpointListParams(TypedDict, total=False):
    after: str
    """Cursor for pagination (ID of the last checkpoint from the previous page)"""

    base_model: str
    """Only return checkpoints trained from this base model. Match is exact."""

    limit: int
    """Maximum number of checkpoints to return (1-100)"""

    session_id: str
    """Only return checkpoints produced by this training session"""
