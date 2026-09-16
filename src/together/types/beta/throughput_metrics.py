# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ThroughputMetrics"]


class ThroughputMetrics(BaseModel):
    """Token, request, and batching throughput over a time range."""

    avg_batch_depth: Optional[float] = FieldInfo(alias="avgBatchDepth", default=None)
    """Average number of batches queued or in flight in the serving engine."""

    avg_batch_size: Optional[float] = FieldInfo(alias="avgBatchSize", default=None)
    """Average number of requests processed in each runtime batch."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average completed requests per second."""

    tokens_per_second: Optional[float] = FieldInfo(alias="tokensPerSecond", default=None)
    """Average generated tokens per second."""
