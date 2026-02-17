# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClusterCreateParams", "SharedVolume"]


class ClusterCreateParams(TypedDict, total=False):
    billing_type: Required[Literal["RESERVED", "ON_DEMAND"]]
    """
    RESERVED billing types allow you to specify the duration of the cluster
    reservation via the duration_days field. ON_DEMAND billing types will give you
    ownership of the cluster until you delete it.
    """

    cluster_name: Required[str]
    """Name of the GPU cluster."""

    driver_version: Required[Literal["CUDA_12_5_555", "CUDA_12_6_560", "CUDA_12_6_565", "CUDA_12_8_570"]]
    """NVIDIA driver version to use in the cluster."""

    gpu_type: Required[Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"]]
    """Type of GPU to use in the cluster"""

    num_gpus: Required[int]
    """Number of GPUs to allocate in the cluster.

    This must be multiple of 8. For example, 8, 16 or 24
    """

    region: Required[str]
    """Region to create the GPU cluster in.

    Usable regions can be found from `client.clusters.list_regions()`
    """

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to create."""

    duration_days: int
    """Duration in days to keep the cluster running."""

    shared_volume: SharedVolume
    """Inline configuration to create a shared volume with the cluster creation."""

    volume_id: str
    """ID of an existing volume to use with the cluster creation."""


class SharedVolume(TypedDict, total=False):
    """Inline configuration to create a shared volume with the cluster creation."""

    region: Required[str]
    """Region name. Usable regions can be found from `client.clusters.list_regions()`"""

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]
    """Customizable name of the volume to create."""
