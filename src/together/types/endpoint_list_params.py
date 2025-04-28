# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EndpointListParams"]


class EndpointListParams(TypedDict, total=False):
    type: Literal["dedicated", "serverless"]
    """Filter endpoints by type"""
