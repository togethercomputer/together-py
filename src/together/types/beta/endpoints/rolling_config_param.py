# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["RollingConfigParam"]


class RollingConfigParam(TypedDict, total=False):
    """
    Rolling strategy configuration for small batches that ramp target replicas up while shrinking source replicas to what their remaining traffic share needs.
    """

    pass
