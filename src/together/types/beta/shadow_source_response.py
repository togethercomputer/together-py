# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .shadow_endpoint_source_response import ShadowEndpointSourceResponse

__all__ = ["ShadowSourceResponse"]


class ShadowSourceResponse(BaseModel):
    """Endpoint traffic source returned for a shadow experiment."""

    endpoint: ShadowEndpointSourceResponse
    """Endpoint-level source returned for a shadow experiment."""
