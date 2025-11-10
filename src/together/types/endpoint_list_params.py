# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EndpointListParams"]


class EndpointListParams(TypedDict, total=False):
    mine: bool
    """If true, return only endpoints owned by the caller"""

    type: Literal["dedicated", "serverless"]
    """Filter endpoints by type"""

    usage_type: Literal["on-demand", "reserved"]
    """Filter endpoints by usage type"""
