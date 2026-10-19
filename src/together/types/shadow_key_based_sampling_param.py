# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ShadowKeyBasedSamplingParam"]


class ShadowKeyBasedSamplingParam(TypedDict, total=False):
    """Fixed-rate sampling of distinct key values with sticky decisions."""

    key: Required[str]
    """Required request-body field used as the sticky sampling key."""

    rate: Required[float]
    """Required fraction of distinct key values to sample, from 0.0 to 1.0."""
