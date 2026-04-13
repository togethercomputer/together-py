# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ClusterCreateParams", "SharedVolume"]


class ClusterCreateParams(TypedDict, total=False):
    billing_type: Required[Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"]]
    """
    RESERVED billing types allow you to specify the duration of the cluster
    reservation via the duration_days field. ON_DEMAND billing types will give you
    ownership of the cluster until you delete it.
    """

    cluster_name: Required[str]
    """Name of the GPU cluster."""

    cuda_version: Required[str]
    """CUDA version for this cluster. For example, 12.5"""

    gpu_type: Required[Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"]]
    """Type of GPU to use in the cluster"""

    num_gpus: Required[int]
    """Number of GPUs to allocate in the cluster.

    This must be multiple of 8. For example, 8, 16 or 24
    """

    nvidia_driver_version: Required[str]
    """Nvidia driver version for this cluster.

    For example, 550. Only some combination of cuda_version and
    nvidia_driver_version are supported.
    """

    region: Required[str]
    """Region to create the GPU cluster in.

    Usable regions can be found from `client.clusters.list_regions()`
    """

    auto_scale_max_gpus: int
    """Maximum number of GPUs to which the cluster can be auto-scaled up.

    This field is required if auto_scaled is true.
    """

    auto_scaled: bool
    """Whether GPU cluster should be auto-scaled based on the workload.

    By default, it is not auto-scaled.
    """

    capacity_pool_id: str
    """ID of the capacity pool to use for the cluster.

    This field is optional and only applicable if the cluster is created from a
    capacity pool.
    """

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to create."""

    duration_days: int
    """Duration in days to keep the cluster running."""

    gpu_node_failover_enabled: bool
    """Whether automated GPU node failover should be enabled for this cluster.

    By default, it is disabled.
    """

    install_traefik: bool
    """Whether to install Traefik ingress controller in the cluster.

    This field is only applicable for Kubernetes clusters and is false by default.
    """

    reservation_end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Reservation end time of the cluster.

    This field is required for SCHEDULED billing to specify the reservation end time
    for the cluster.
    """

    reservation_start_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Reservation start time of the cluster.

    This field is required for SCHEDULED billing to specify the reservation start
    time for the cluster. If not provided, the cluster will be provisioned
    immediately.
    """

    shared_volume: SharedVolume
    """Inline configuration to create a shared volume with the cluster creation."""

    slurm_image: str
    """Custom Slurm image for Slurm clusters."""

    slurm_shm_size_gib: int
    """Shared memory size in GiB for Slurm cluster.

    This field is required if cluster_type is SLURM.
    """

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
