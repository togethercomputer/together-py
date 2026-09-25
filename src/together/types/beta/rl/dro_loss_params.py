# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["DroLossParams"]


class DroLossParams(TypedDict, total=False):
    beta: Required[float]
    """Coefficient on the quadratic log-ratio penalty. Required; there is no default."""
