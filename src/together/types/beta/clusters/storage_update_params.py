# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StorageUpdateParams"]


class StorageUpdateParams(TypedDict, total=False):
    volume_id: Required[str]
    """ID of the volume."""

    size_tib: int
    """Size of the volume in TiB."""
