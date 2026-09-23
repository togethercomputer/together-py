# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ShadowUniformSamplingResponse"]


class ShadowUniformSamplingResponse(BaseModel):
    """Fixed-rate random sampling returned by the API.

    A zero rate may be omitted by JSON serialization.
    """

    rate: Optional[float] = None
    """Fraction of requests sampled, from 0.0 to 1.0."""
