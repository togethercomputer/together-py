# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .error_metrics import ErrorMetrics
from .token_metrics import TokenMetrics
from .latency_metrics import LatencyMetrics
from .request_metrics import RequestMetrics
from .metrics_time_range import MetricsTimeRange
from .throughput_metrics import ThroughputMetrics
from .resource_utilization import ResourceUtilization

__all__ = ["DeploymentMetrics"]


class DeploymentMetrics(BaseModel):
    """Operational metrics for one deployment under an endpoint."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment summarized by these metrics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the deployment's parent endpoint."""

    error_metrics: Optional[ErrorMetrics] = FieldInfo(alias="errorMetrics", default=None)
    """Error rate and counts by error type."""

    latency_metrics: Optional[LatencyMetrics] = FieldInfo(alias="latencyMetrics", default=None)
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    request_metrics: Optional[RequestMetrics] = FieldInfo(alias="requestMetrics", default=None)
    """Request counts and rates."""

    resource_utilization: Optional[ResourceUtilization] = FieldInfo(alias="resourceUtilization", default=None)
    """Average CPU, GPU, memory, and network utilization."""

    throughput_metrics: Optional[ThroughputMetrics] = FieldInfo(alias="throughputMetrics", default=None)
    """Token, request, and batching throughput."""

    time_range: Optional[MetricsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the metrics."""

    token_metrics: Optional[TokenMetrics] = FieldInfo(alias="tokenMetrics", default=None)
    """Input and output token totals and averages."""
