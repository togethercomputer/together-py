# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ShadowAdaptiveUniformSamplingResponse"]


class ShadowAdaptiveUniformSamplingResponse(BaseModel):
    """Adaptive random sampling returned by the API."""

    target_qps: float = FieldInfo(alias="targetQps")
    """Per-gateway-replica target QPS."""

    window: Optional[str] = None
    """Sliding window for QPS observation when explicitly configured."""
