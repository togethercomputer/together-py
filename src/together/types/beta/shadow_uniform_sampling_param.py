# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ShadowUniformSamplingParam"]


class ShadowUniformSamplingParam(TypedDict, total=False):
    """Fixed-rate random sampling of endpoint requests."""

    rate: Required[float]
    """Required fraction of requests to sample, from 0.0 to 1.0."""
