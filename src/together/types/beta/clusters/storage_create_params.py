# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StorageCreateParams"]


class StorageCreateParams(TypedDict, total=False):
    region: Required[str]

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]

    is_lifecycle_independent: bool
    """When true, the shared volume is not deleted when the cluster is decommissioned."""
