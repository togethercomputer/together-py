# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ShadowAdaptiveKeyBasedSamplingParam"]


class ShadowAdaptiveKeyBasedSamplingParam(TypedDict, total=False):
    """Adaptive sticky-key sampling that throttles toward a target QPS."""

    key: Required[str]
    """Required request-body field used as the sticky sampling key."""

    target_qps: Required[Annotated[float, PropertyInfo(alias="targetQps")]]
    """Required per-gateway-replica target QPS for adaptive sampling."""

    window: str
    """Optional sliding window for QPS observation.

    Defaults to 60s and must not be negative.
    """
