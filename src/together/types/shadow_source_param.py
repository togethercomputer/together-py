# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .shadow_endpoint_source_param import ShadowEndpointSourceParam

__all__ = ["ShadowSourceParam"]


class ShadowSourceParam(TypedDict, total=False):
    """Traffic source for a shadow experiment.

    The public API supports endpoint sources only.
    """

    endpoint: Required[ShadowEndpointSourceParam]
    """Endpoint-level source that samples endpoint traffic at the API gateway."""
