# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["AutoscalingParam"]


class AutoscalingParam(TypedDict, total=False):
    """Configuration for automatic scaling of replicas based on demand."""

    max_replicas: Required[int]
    """The maximum number of replicas to scale up to under load"""

    min_replicas: Required[int]
    """The minimum number of replicas to maintain, even when there is no load"""
