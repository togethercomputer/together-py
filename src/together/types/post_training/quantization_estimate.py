# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["QuantizationEstimate"]


class QuantizationEstimate(BaseModel):
    """Price and duration estimate for a quantization job."""

    allowed_to_proceed: bool
    """Whether a create request at this price would be accepted."""

    credit_limit: float
    """Project credit limit in US dollars."""

    price_usd: float
    """Expected total run cost in US dollars."""

    time_hours: float
    """Expected wall-clock run time in hours, excluding queue time."""
