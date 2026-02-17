# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["StorageUpdateParams"]


class StorageUpdateParams(TypedDict, total=False):
    size_tib: int
    """Size of the volume in whole tebibytes (TiB)."""

    volume_id: str
    """ID of the volume to update."""
