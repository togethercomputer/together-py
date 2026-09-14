# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = [
    "EndpointAnalyticsResponse",
    "DeploymentAnalytics",
    "DeploymentAnalyticsMetrics",
    "DeploymentAnalyticsMetricsErrorMetrics",
    "DeploymentAnalyticsMetricsLatencyMetrics",
    "DeploymentAnalyticsMetricsRequestMetrics",
    "DeploymentAnalyticsMetricsResourceUtilization",
    "DeploymentAnalyticsMetricsThroughputMetrics",
    "DeploymentAnalyticsMetricsTimeRange",
    "DeploymentAnalyticsMetricsTokenMetrics",
    "DeploymentAnalyticsTimeRange",
    "DeploymentAnalyticsTimeSeries",
    "Metrics",
    "MetricsDeploymentMetric",
    "MetricsDeploymentMetricErrorMetrics",
    "MetricsDeploymentMetricLatencyMetrics",
    "MetricsDeploymentMetricRequestMetrics",
    "MetricsDeploymentMetricResourceUtilization",
    "MetricsDeploymentMetricThroughputMetrics",
    "MetricsDeploymentMetricTimeRange",
    "MetricsDeploymentMetricTokenMetrics",
    "MetricsErrorMetrics",
    "MetricsLatencyMetrics",
    "MetricsRequestMetrics",
    "MetricsResourceUtilization",
    "MetricsThroughputMetrics",
    "MetricsTimeRange",
    "MetricsTokenMetrics",
    "TimeRange",
    "TimeSeries",
]


class DeploymentAnalyticsMetricsErrorMetrics(BaseModel):
    """Error rate and counts by error type."""

    error_rate: Optional[float] = FieldInfo(alias="errorRate", default=None)
    """Percentage in [0, 100]."""

    errors_by_type: Optional[Dict[str, str]] = FieldInfo(alias="errorsByType", default=None)
    """Counts of errors keyed by error type (e.g. HTTP status code or error kind)."""


class DeploymentAnalyticsMetricsLatencyMetrics(BaseModel):
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    itl_p50_ms: Optional[float] = FieldInfo(alias="itlP50Ms", default=None)
    """50th-percentile inter-token latency, in milliseconds."""

    itl_p90_ms: Optional[float] = FieldInfo(alias="itlP90Ms", default=None)
    """90th-percentile inter-token latency, in milliseconds."""

    itl_p99_ms: Optional[float] = FieldInfo(alias="itlP99Ms", default=None)
    """99th-percentile inter-token latency, in milliseconds."""

    latency_p50_ms: Optional[float] = FieldInfo(alias="latencyP50Ms", default=None)
    """50th-percentile end-to-end request latency, in milliseconds."""

    latency_p90_ms: Optional[float] = FieldInfo(alias="latencyP90Ms", default=None)
    """90th-percentile end-to-end request latency, in milliseconds."""

    latency_p99_ms: Optional[float] = FieldInfo(alias="latencyP99Ms", default=None)
    """99th-percentile end-to-end request latency, in milliseconds."""

    ttft_p50_ms: Optional[float] = FieldInfo(alias="ttftP50Ms", default=None)
    """50th-percentile time to first token, in milliseconds."""

    ttft_p90_ms: Optional[float] = FieldInfo(alias="ttftP90Ms", default=None)
    """90th-percentile time to first token, in milliseconds."""

    ttft_p99_ms: Optional[float] = FieldInfo(alias="ttftP99Ms", default=None)
    """99th-percentile time to first token, in milliseconds."""


class DeploymentAnalyticsMetricsRequestMetrics(BaseModel):
    """Request counts and rates."""

    failed_requests: Optional[str] = FieldInfo(alias="failedRequests", default=None)
    """Requests that failed during the time range."""

    requests_by_status_code: Optional[Dict[str, str]] = FieldInfo(alias="requestsByStatusCode", default=None)
    """Request counts keyed by HTTP status code."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average requests per second over the time range."""

    successful_requests: Optional[str] = FieldInfo(alias="successfulRequests", default=None)
    """Requests completed successfully during the time range."""

    total_requests: Optional[str] = FieldInfo(alias="totalRequests", default=None)
    """Total requests received during the time range."""


class DeploymentAnalyticsMetricsResourceUtilization(BaseModel):
    """Average CPU, GPU, memory, and network utilization."""

    cpu_utilization: Optional[float] = FieldInfo(alias="cpuUtilization", default=None)
    """Average CPU utilization across replicas, as a percentage."""

    gpu_memory_utilization: Optional[float] = FieldInfo(alias="gpuMemoryUtilization", default=None)
    """Average GPU memory utilization across replicas, as a percentage."""

    gpu_utilization: Optional[float] = FieldInfo(alias="gpuUtilization", default=None)
    """Average GPU compute utilization across replicas, as a percentage."""

    memory_utilization: Optional[float] = FieldInfo(alias="memoryUtilization", default=None)
    """Average system memory utilization across replicas, as a percentage."""

    network_bandwidth_mbps: Optional[float] = FieldInfo(alias="networkBandwidthMbps", default=None)
    """Average network throughput across replicas, in megabits per second."""


class DeploymentAnalyticsMetricsThroughputMetrics(BaseModel):
    """Token, request, and batching throughput."""

    avg_batch_depth: Optional[float] = FieldInfo(alias="avgBatchDepth", default=None)
    """Average number of batches queued or in flight in the serving engine."""

    avg_batch_size: Optional[float] = FieldInfo(alias="avgBatchSize", default=None)
    """Average number of requests processed in each runtime batch."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average completed requests per second."""

    tokens_per_second: Optional[float] = FieldInfo(alias="tokensPerSecond", default=None)
    """Average generated tokens per second."""


class DeploymentAnalyticsMetricsTimeRange(BaseModel):
    """Closed-open time range covered by the metrics."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""


class DeploymentAnalyticsMetricsTokenMetrics(BaseModel):
    """Input and output token totals and averages."""

    avg_input_tokens: Optional[float] = FieldInfo(alias="avgInputTokens", default=None)
    """Average input tokens per request."""

    avg_output_tokens: Optional[float] = FieldInfo(alias="avgOutputTokens", default=None)
    """Average output tokens per request."""

    total_input_tokens: Optional[str] = FieldInfo(alias="totalInputTokens", default=None)
    """Total input tokens processed during the time range."""

    total_output_tokens: Optional[str] = FieldInfo(alias="totalOutputTokens", default=None)
    """Total output tokens generated during the time range."""


class DeploymentAnalyticsMetrics(BaseModel):
    """Aggregate operational metrics for the deployment."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment summarized by these metrics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the deployment's parent endpoint."""

    error_metrics: Optional[DeploymentAnalyticsMetricsErrorMetrics] = FieldInfo(alias="errorMetrics", default=None)
    """Error rate and counts by error type."""

    latency_metrics: Optional[DeploymentAnalyticsMetricsLatencyMetrics] = FieldInfo(
        alias="latencyMetrics", default=None
    )
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    request_metrics: Optional[DeploymentAnalyticsMetricsRequestMetrics] = FieldInfo(
        alias="requestMetrics", default=None
    )
    """Request counts and rates."""

    resource_utilization: Optional[DeploymentAnalyticsMetricsResourceUtilization] = FieldInfo(
        alias="resourceUtilization", default=None
    )
    """Average CPU, GPU, memory, and network utilization."""

    throughput_metrics: Optional[DeploymentAnalyticsMetricsThroughputMetrics] = FieldInfo(
        alias="throughputMetrics", default=None
    )
    """Token, request, and batching throughput."""

    time_range: Optional[DeploymentAnalyticsMetricsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the metrics."""

    token_metrics: Optional[DeploymentAnalyticsMetricsTokenMetrics] = FieldInfo(alias="tokenMetrics", default=None)
    """Input and output token totals and averages."""


class DeploymentAnalyticsTimeRange(BaseModel):
    """Closed-open time range covered by the analytics."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""


class DeploymentAnalyticsTimeSeries(BaseModel):
    """Timestamped bucket containing one or more named metric values."""

    timestamp: Optional[datetime] = None
    """Start time of the metric bucket."""

    values: Optional[Dict[str, float]] = None
    """Metric names mapped to their numeric values for this bucket."""


class DeploymentAnalytics(BaseModel):
    """Usage and performance analytics for one deployment under an endpoint."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment summarized by these analytics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the deployment's parent endpoint."""

    metrics: Optional[DeploymentAnalyticsMetrics] = None
    """Aggregate operational metrics for the deployment."""

    time_range: Optional[DeploymentAnalyticsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the analytics."""

    time_series: Optional[List[DeploymentAnalyticsTimeSeries]] = FieldInfo(alias="timeSeries", default=None)
    """Per-bucket metric samples for the deployment."""


class MetricsDeploymentMetricErrorMetrics(BaseModel):
    """Error rate and counts by error type."""

    error_rate: Optional[float] = FieldInfo(alias="errorRate", default=None)
    """Percentage in [0, 100]."""

    errors_by_type: Optional[Dict[str, str]] = FieldInfo(alias="errorsByType", default=None)
    """Counts of errors keyed by error type (e.g. HTTP status code or error kind)."""


class MetricsDeploymentMetricLatencyMetrics(BaseModel):
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    itl_p50_ms: Optional[float] = FieldInfo(alias="itlP50Ms", default=None)
    """50th-percentile inter-token latency, in milliseconds."""

    itl_p90_ms: Optional[float] = FieldInfo(alias="itlP90Ms", default=None)
    """90th-percentile inter-token latency, in milliseconds."""

    itl_p99_ms: Optional[float] = FieldInfo(alias="itlP99Ms", default=None)
    """99th-percentile inter-token latency, in milliseconds."""

    latency_p50_ms: Optional[float] = FieldInfo(alias="latencyP50Ms", default=None)
    """50th-percentile end-to-end request latency, in milliseconds."""

    latency_p90_ms: Optional[float] = FieldInfo(alias="latencyP90Ms", default=None)
    """90th-percentile end-to-end request latency, in milliseconds."""

    latency_p99_ms: Optional[float] = FieldInfo(alias="latencyP99Ms", default=None)
    """99th-percentile end-to-end request latency, in milliseconds."""

    ttft_p50_ms: Optional[float] = FieldInfo(alias="ttftP50Ms", default=None)
    """50th-percentile time to first token, in milliseconds."""

    ttft_p90_ms: Optional[float] = FieldInfo(alias="ttftP90Ms", default=None)
    """90th-percentile time to first token, in milliseconds."""

    ttft_p99_ms: Optional[float] = FieldInfo(alias="ttftP99Ms", default=None)
    """99th-percentile time to first token, in milliseconds."""


class MetricsDeploymentMetricRequestMetrics(BaseModel):
    """Request counts and rates."""

    failed_requests: Optional[str] = FieldInfo(alias="failedRequests", default=None)
    """Requests that failed during the time range."""

    requests_by_status_code: Optional[Dict[str, str]] = FieldInfo(alias="requestsByStatusCode", default=None)
    """Request counts keyed by HTTP status code."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average requests per second over the time range."""

    successful_requests: Optional[str] = FieldInfo(alias="successfulRequests", default=None)
    """Requests completed successfully during the time range."""

    total_requests: Optional[str] = FieldInfo(alias="totalRequests", default=None)
    """Total requests received during the time range."""


class MetricsDeploymentMetricResourceUtilization(BaseModel):
    """Average CPU, GPU, memory, and network utilization."""

    cpu_utilization: Optional[float] = FieldInfo(alias="cpuUtilization", default=None)
    """Average CPU utilization across replicas, as a percentage."""

    gpu_memory_utilization: Optional[float] = FieldInfo(alias="gpuMemoryUtilization", default=None)
    """Average GPU memory utilization across replicas, as a percentage."""

    gpu_utilization: Optional[float] = FieldInfo(alias="gpuUtilization", default=None)
    """Average GPU compute utilization across replicas, as a percentage."""

    memory_utilization: Optional[float] = FieldInfo(alias="memoryUtilization", default=None)
    """Average system memory utilization across replicas, as a percentage."""

    network_bandwidth_mbps: Optional[float] = FieldInfo(alias="networkBandwidthMbps", default=None)
    """Average network throughput across replicas, in megabits per second."""


class MetricsDeploymentMetricThroughputMetrics(BaseModel):
    """Token, request, and batching throughput."""

    avg_batch_depth: Optional[float] = FieldInfo(alias="avgBatchDepth", default=None)
    """Average number of batches queued or in flight in the serving engine."""

    avg_batch_size: Optional[float] = FieldInfo(alias="avgBatchSize", default=None)
    """Average number of requests processed in each runtime batch."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average completed requests per second."""

    tokens_per_second: Optional[float] = FieldInfo(alias="tokensPerSecond", default=None)
    """Average generated tokens per second."""


class MetricsDeploymentMetricTimeRange(BaseModel):
    """Closed-open time range covered by the metrics."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""


class MetricsDeploymentMetricTokenMetrics(BaseModel):
    """Input and output token totals and averages."""

    avg_input_tokens: Optional[float] = FieldInfo(alias="avgInputTokens", default=None)
    """Average input tokens per request."""

    avg_output_tokens: Optional[float] = FieldInfo(alias="avgOutputTokens", default=None)
    """Average output tokens per request."""

    total_input_tokens: Optional[str] = FieldInfo(alias="totalInputTokens", default=None)
    """Total input tokens processed during the time range."""

    total_output_tokens: Optional[str] = FieldInfo(alias="totalOutputTokens", default=None)
    """Total output tokens generated during the time range."""


class MetricsDeploymentMetric(BaseModel):
    """Operational metrics for one deployment under an endpoint."""

    deployment_id: Optional[str] = FieldInfo(alias="deploymentId", default=None)
    """ID of the deployment summarized by these metrics."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """ID of the deployment's parent endpoint."""

    error_metrics: Optional[MetricsDeploymentMetricErrorMetrics] = FieldInfo(alias="errorMetrics", default=None)
    """Error rate and counts by error type."""

    latency_metrics: Optional[MetricsDeploymentMetricLatencyMetrics] = FieldInfo(alias="latencyMetrics", default=None)
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    request_metrics: Optional[MetricsDeploymentMetricRequestMetrics] = FieldInfo(alias="requestMetrics", default=None)
    """Request counts and rates."""

    resource_utilization: Optional[MetricsDeploymentMetricResourceUtilization] = FieldInfo(
        alias="resourceUtilization", default=None
    )
    """Average CPU, GPU, memory, and network utilization."""

    throughput_metrics: Optional[MetricsDeploymentMetricThroughputMetrics] = FieldInfo(
        alias="throughputMetrics", default=None
    )
    """Token, request, and batching throughput."""

    time_range: Optional[MetricsDeploymentMetricTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the metrics."""

    token_metrics: Optional[MetricsDeploymentMetricTokenMetrics] = FieldInfo(alias="tokenMetrics", default=None)
    """Input and output token totals and averages."""


class MetricsErrorMetrics(BaseModel):
    """Error rate and counts by error type."""

    error_rate: Optional[float] = FieldInfo(alias="errorRate", default=None)
    """Percentage in [0, 100]."""

    errors_by_type: Optional[Dict[str, str]] = FieldInfo(alias="errorsByType", default=None)
    """Counts of errors keyed by error type (e.g. HTTP status code or error kind)."""


class MetricsLatencyMetrics(BaseModel):
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    itl_p50_ms: Optional[float] = FieldInfo(alias="itlP50Ms", default=None)
    """50th-percentile inter-token latency, in milliseconds."""

    itl_p90_ms: Optional[float] = FieldInfo(alias="itlP90Ms", default=None)
    """90th-percentile inter-token latency, in milliseconds."""

    itl_p99_ms: Optional[float] = FieldInfo(alias="itlP99Ms", default=None)
    """99th-percentile inter-token latency, in milliseconds."""

    latency_p50_ms: Optional[float] = FieldInfo(alias="latencyP50Ms", default=None)
    """50th-percentile end-to-end request latency, in milliseconds."""

    latency_p90_ms: Optional[float] = FieldInfo(alias="latencyP90Ms", default=None)
    """90th-percentile end-to-end request latency, in milliseconds."""

    latency_p99_ms: Optional[float] = FieldInfo(alias="latencyP99Ms", default=None)
    """99th-percentile end-to-end request latency, in milliseconds."""

    ttft_p50_ms: Optional[float] = FieldInfo(alias="ttftP50Ms", default=None)
    """50th-percentile time to first token, in milliseconds."""

    ttft_p90_ms: Optional[float] = FieldInfo(alias="ttftP90Ms", default=None)
    """90th-percentile time to first token, in milliseconds."""

    ttft_p99_ms: Optional[float] = FieldInfo(alias="ttftP99Ms", default=None)
    """99th-percentile time to first token, in milliseconds."""


class MetricsRequestMetrics(BaseModel):
    """Request counts and rates."""

    failed_requests: Optional[str] = FieldInfo(alias="failedRequests", default=None)
    """Requests that failed during the time range."""

    requests_by_status_code: Optional[Dict[str, str]] = FieldInfo(alias="requestsByStatusCode", default=None)
    """Request counts keyed by HTTP status code."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average requests per second over the time range."""

    successful_requests: Optional[str] = FieldInfo(alias="successfulRequests", default=None)
    """Requests completed successfully during the time range."""

    total_requests: Optional[str] = FieldInfo(alias="totalRequests", default=None)
    """Total requests received during the time range."""


class MetricsResourceUtilization(BaseModel):
    """Average CPU, GPU, memory, and network utilization."""

    cpu_utilization: Optional[float] = FieldInfo(alias="cpuUtilization", default=None)
    """Average CPU utilization across replicas, as a percentage."""

    gpu_memory_utilization: Optional[float] = FieldInfo(alias="gpuMemoryUtilization", default=None)
    """Average GPU memory utilization across replicas, as a percentage."""

    gpu_utilization: Optional[float] = FieldInfo(alias="gpuUtilization", default=None)
    """Average GPU compute utilization across replicas, as a percentage."""

    memory_utilization: Optional[float] = FieldInfo(alias="memoryUtilization", default=None)
    """Average system memory utilization across replicas, as a percentage."""

    network_bandwidth_mbps: Optional[float] = FieldInfo(alias="networkBandwidthMbps", default=None)
    """Average network throughput across replicas, in megabits per second."""


class MetricsThroughputMetrics(BaseModel):
    """Token, request, and batching throughput."""

    avg_batch_depth: Optional[float] = FieldInfo(alias="avgBatchDepth", default=None)
    """Average number of batches queued or in flight in the serving engine."""

    avg_batch_size: Optional[float] = FieldInfo(alias="avgBatchSize", default=None)
    """Average number of requests processed in each runtime batch."""

    requests_per_second: Optional[float] = FieldInfo(alias="requestsPerSecond", default=None)
    """Average completed requests per second."""

    tokens_per_second: Optional[float] = FieldInfo(alias="tokensPerSecond", default=None)
    """Average generated tokens per second."""


class MetricsTimeRange(BaseModel):
    """Closed-open time range used by metrics and analytics responses."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""


class MetricsTokenMetrics(BaseModel):
    """Input and output token totals and averages."""

    avg_input_tokens: Optional[float] = FieldInfo(alias="avgInputTokens", default=None)
    """Average input tokens per request."""

    avg_output_tokens: Optional[float] = FieldInfo(alias="avgOutputTokens", default=None)
    """Average output tokens per request."""

    total_input_tokens: Optional[str] = FieldInfo(alias="totalInputTokens", default=None)
    """Total input tokens processed during the time range."""

    total_output_tokens: Optional[str] = FieldInfo(alias="totalOutputTokens", default=None)
    """Total output tokens generated during the time range."""


class Metrics(BaseModel):
    """
    Operational metrics aggregated across all deployments receiving traffic for an endpoint.
    """

    deployment_metrics: Optional[List[MetricsDeploymentMetric]] = FieldInfo(alias="deploymentMetrics", default=None)
    """Per-deployment breakdown, if the endpoint has multiple deployments."""

    endpoint_id: Optional[str] = FieldInfo(alias="endpointId", default=None)
    """The endpoint these metrics describe."""

    error_metrics: Optional[MetricsErrorMetrics] = FieldInfo(alias="errorMetrics", default=None)
    """Error rate and counts by error type."""

    latency_metrics: Optional[MetricsLatencyMetrics] = FieldInfo(alias="latencyMetrics", default=None)
    """Time-to-first-token, end-to-end, and inter-token latency percentiles."""

    request_metrics: Optional[MetricsRequestMetrics] = FieldInfo(alias="requestMetrics", default=None)
    """Request counts and rates."""

    resource_utilization: Optional[MetricsResourceUtilization] = FieldInfo(alias="resourceUtilization", default=None)
    """Average CPU, GPU, memory, and network utilization."""

    throughput_metrics: Optional[MetricsThroughputMetrics] = FieldInfo(alias="throughputMetrics", default=None)
    """Token, request, and batching throughput."""

    time_range: Optional[MetricsTimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range used by metrics and analytics responses."""

    token_metrics: Optional[MetricsTokenMetrics] = FieldInfo(alias="tokenMetrics", default=None)
    """Input and output token totals and averages."""


class TimeRange(BaseModel):
    """Closed-open time range covered by the analytics."""

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)
    """Exclusive end of the time range."""

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)
    """Inclusive start of the time range."""


class TimeSeries(BaseModel):
    """Timestamped bucket containing one or more named metric values."""

    timestamp: Optional[datetime] = None
    """Start time of the metric bucket."""

    values: Optional[Dict[str, float]] = None
    """Metric names mapped to their numeric values for this bucket."""


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

    time_range: Optional[TimeRange] = FieldInfo(alias="timeRange", default=None)
    """Closed-open time range covered by the analytics."""

    time_series: Optional[List[TimeSeries]] = FieldInfo(alias="timeSeries", default=None)
    """Per-bucket metric samples, included only when `includeTimeSeries` is true."""
