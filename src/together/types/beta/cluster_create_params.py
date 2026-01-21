# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClusterCreateParams", "SharedVolume"]


class ClusterCreateParams(TypedDict, total=False):
    billing_type: Required[Literal["RESERVED", "ON_DEMAND"]]

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

    region: Required[Literal["us-central-8", "us-central-4"]]
    """Region to create the GPU cluster in.

    Valid values are us-central-8 and us-central-4.
    """

    cluster_type: Literal["KUBERNETES", "SLURM"]

    duration_days: int
    """Duration in days to keep the cluster running."""

    shared_volume: SharedVolume

    volume_id: str


class SharedVolume(TypedDict, total=False):
    region: Required[str]
    """Region name. Usable regions can be found from `client.clusters.list_regions()`"""

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]
