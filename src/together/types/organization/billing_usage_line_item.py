# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from ..._models import BaseModel

__all__ = ["BillingUsageLineItem"]


class BillingUsageLineItem(BaseModel):
    attributes: Dict[str, str]
    """Resource identifiers for attribution, varying by product."""

    cost: str
    """Total cost for this line item in USD as a decimal string."""

    pricing_dimensions: Dict[str, str]
    """Rate-determining dimensions (varies by product).

    Passthrough from Metronome pricing group values.
    """

    product_name: str
    """Metronome product name (e.g. 'Serverless Inference - Input Tokens')."""

    quantity: str
    """
    Total usage for the window in the product's native unit (GPU-hours, tokens, ...)
    as a decimal string.
    """

    unit_price: str
    """Per-unit price in USD as a decimal string."""
