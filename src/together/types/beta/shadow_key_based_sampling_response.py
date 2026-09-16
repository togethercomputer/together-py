# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ShadowKeyBasedSamplingResponse"]


class ShadowKeyBasedSamplingResponse(BaseModel):
    """Fixed-rate sticky-key sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """

    key: str
    """Request-body field used as the sticky sampling key."""

    rate: Optional[float] = None
    """Fraction of distinct key values sampled, from 0.0 to 1.0."""
