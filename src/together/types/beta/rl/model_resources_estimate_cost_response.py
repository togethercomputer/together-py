# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["ModelResourcesEstimateCostResponse"]


class ModelResourcesEstimateCostResponse(BaseModel):
    currency: str
    """ISO 4217 currency code."""

    price_per_hour: float
    """Estimated on-demand price per hour in the currency's major unit."""
