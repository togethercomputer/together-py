# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["ThresholdCheck"]


class ThresholdCheck(BaseModel):
    """
    Threshold criteria that fail when the target metric violates the configured bound.
    """

    operator: Literal[
        "THRESHOLD_OPERATOR_GT", "THRESHOLD_OPERATOR_GTE", "THRESHOLD_OPERATOR_LT", "THRESHOLD_OPERATOR_LTE"
    ]
    """Required comparison operator applied to the target metric value."""

    value: Optional[float] = None
    """Finite threshold value.

    Interpreted in the metric's unit: router_error_rate is a ratio in [0, 1],
    router_latency is milliseconds, and inflight_requests is in-flight requests per
    ready replica averaged over the rule window. Thresholds that no achievable value
    could pass, or that every achievable value passes, are rejected at create.

    Omitting this value is read as 0. Set 0 explicitly for the strictest threshold:
    nothing at all is tolerated.
    """
