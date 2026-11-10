# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["RollingConfigParam"]


class RollingConfigParam(TypedDict, total=False):
    """Rolling strategy configuration.

    The target ramps up one replica per rung while the source shrinks to what its remaining traffic share needs.
    """

    pass
