# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .error_metrics import ErrorMetrics
from .token_metrics import TokenMetrics
from .latency_metrics import LatencyMetrics
from .request_metrics import RequestMetrics
from .deployment_metrics import DeploymentMetrics
from .metrics_time_range import MetricsTimeRange
from .throughput_metrics import ThroughputMetrics
from .resource_utilization import ResourceUtilization
from .time_series_data_point import TimeSeriesDataPoint

__all__ = ["EndpointAnalyticsResponse", "DeploymentAnalytics", "Metrics"]


class DeploymentAnalytics(BaseModel):
    """Usage and performance analytics for one deployment under an endpoint."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment summarized by these analytics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the deployment's parent endpoint."""

    metrics: Optional[DeploymentMetrics] = None
    """Aggregate operational metrics for the deployment."""

    time_range: Optional[MetricsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the analytics."""

    time_series: Optional[List[TimeSeriesDataPoint]] = FieldInfo(alias="timeSeries", default=None)
    """Per-bucket metric samples for the deployment."""


class Metrics(BaseModel):
    """
    Operational metrics aggregated across all deployments receiving traffic for an endpoint.
    """

    deployment_metrics: Optional[List[DeploymentMetrics]] = FieldInfo(alias="deploymentMetrics", default=None)
    """Per-deployment breakdown, if the endpoint has multiple deployments."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """The endpoint these metrics describe."""

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
    """Closed-open time range used by metrics and analytics responses."""

    token_metrics: Optional[TokenMetrics] = FieldInfo(alias="tokenMetrics", default=None)
    """Input and output token totals and averages."""


class EndpointAnalyticsResponse(BaseModel):
    """
    Endpoint-wide usage and performance analytics with optional time-series and per-deployment breakdowns.
    """

    deployment_analytics: Optional[List[DeploymentAnalytics]] = FieldInfo(alias="deploymentAnalytics", default=None)
    """Per-deployment analytics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the endpoint summarized by these analytics."""

    metrics: Optional[Metrics] = None
    """
    Operational metrics aggregated across all deployments receiving traffic for an
    endpoint.
    """

    time_range: Optional[MetricsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the analytics."""

    time_series: Optional[List[TimeSeriesDataPoint]] = FieldInfo(alias="timeSeries", default=None)
    """Per-bucket metric samples, included only when `includeTimeSeries` is true."""
