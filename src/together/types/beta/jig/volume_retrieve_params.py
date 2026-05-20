# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["VolumeRetrieveParams"]


class VolumeRetrieveParams(TypedDict, total=False):
    version: int
    """Volume version to describe (defaults to current version)"""
