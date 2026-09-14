# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ModelListParams"]


class ModelListParams(TypedDict, total=False):
    dedicated: bool
    """Filter models to only return dedicated models"""
