# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["StorageCreateParams"]


class StorageCreateParams(TypedDict, total=False):
    region: Required[str]
    """Region name. Usable regions can be found from `clusters.list_regions()`"""

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]
    """User provided name of the volume."""

    instance_cluster_id: str
    """Cluster ID to pin the volume to the same substrate as that GPU cluster."""

    is_lifecycle_independent: bool
    """When true, the shared volume is not deleted when the cluster is decommissioned."""

    project_id: str
    """Project ID that will own the volume.

    When omitted, the caller's default project is used.
    """
