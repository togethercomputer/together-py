# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["QueueMetricsResponse"]


class QueueMetricsResponse(BaseModel):
    messages_running: int
    """Number of jobs currently being processed"""

    messages_waiting: int
    """Number of jobs waiting to be claimed by a worker"""

    total_jobs: int
    """Total number of active jobs (waiting + running)"""
