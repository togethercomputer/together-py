# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelResourceExtendExpiryParams"]


class ModelResourceExtendExpiryParams(TypedDict, total=False):
    minutes: Required[int]
    """Minutes from now the resource must not stop for inactivity."""
