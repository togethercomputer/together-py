# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StorageCreateParams"]


class StorageCreateParams(TypedDict, total=False):
    region: Required[str]
    """Region name. Usable regions can be found from `client.clusters.list_regions()`"""

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]
