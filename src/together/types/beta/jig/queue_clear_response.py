# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["QueueClearResponse"]


class QueueClearResponse(BaseModel):
    """Count of pending jobs canceled by the clear operation."""

    canceled_count: int
    """Number of pending jobs that were canceled"""
