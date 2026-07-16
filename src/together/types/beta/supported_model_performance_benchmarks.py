# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SupportedModelPerformanceBenchmarks"]


class SupportedModelPerformanceBenchmarks(BaseModel):
    """Performance benchmark metrics for a supported model profile."""

    decoding_speed_tps: Optional[float] = FieldInfo(alias="decodingSpeedTps", default=None)
    """Decoding throughput in tokens per second."""

    max_context_length: Optional[str] = FieldInfo(alias="maxContextLength", default=None)
    """Maximum context length supported by the profile."""

    time_to_first_token_ms: Optional[int] = FieldInfo(alias="timeToFirstTokenMs", default=None)
    """Time to first token in milliseconds."""
