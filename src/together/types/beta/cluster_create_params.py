# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "ClusterCreateParams",
    "AcceptanceTestsParams",
    "AddOn",
    "AddOnConfig",
    "AddOnConfigDashboard",
    "AddOnConfigIngress",
    "ClusterConfig",
    "ClusterConfigIngress",
    "ClusterConfigObservability",
    "ClusterConfigSlurmStartupScripts",
    "OidcConfig",
    "SharedVolume",
]


class ClusterCreateParams(TypedDict, total=False):
    billing_type: Required[Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"]]
    """
    RESERVED billing types allow you to specify the duration of the cluster
    reservation via the duration_days field. ON_DEMAND billing types will give you
    ownership of the cluster until you delete it. SCHEDULED_CAPACITY billing types
    allow you to reserve capacity for a scheduled time window. You must specify the
    reservation_start_time and reservation_end_time with this request.
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

    acceptance_tests_params: AcceptanceTestsParams
    """
    AcceptanceTestsParams groups all GPU acceptance test options when enabled is
    true.
    """

    add_ons: Iterable[AddOn]
    """Add-ons to enable on the cluster at creation time."""

    auto_scale: bool
    """Whether to enable auto-scaling for the cluster.

    If true, the cluster will automatically scale the number of GPU worker nodes
    between num_gpus and auto_scale_max_gpus based on the workload.
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

    cluster_config: ClusterConfig

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to create."""

    duration_days: int
    """Duration in days to keep the cluster running."""

    install_traefik: bool
    """Whether to install Traefik ingress controller in the cluster.

    This field is only applicable for Kubernetes clusters and is false by default.
    """

    num_capacity_pool_gpus: int
    """Number of GPUs to allocate from the capacity pool.

    Must be a multiple of 8 and not exceed num_gpus.
    """

    num_preemptible_gpus: int
    """Number of preemptible GPUs to request alongside on-demand capacity.

    Must be a multiple of 8. Preemptible nodes are cheaper but may be reclaimed when
    on-demand capacity is needed elsewhere; the system fulfills this asynchronously
    and surfaces the actual count in allocated_preemptible_gpus.
    """

    num_reserved_gpus: int
    """Number of prepaid (PLG) reserved GPUs for this cluster.

    When omitted for RESERVED billing on create, the server defaults this to
    num_gpus.
    """

    oidc_config: OidcConfig

    project_id: str
    """Project ID for the cluster.

    If not set, the project from the request context is used.
    """

    reservation_end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Reservation end time of the cluster.

    This field is required for SCHEDULED billing to specify the reservation end time
    for the cluster.
    """

    reservation_start_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Reservation start time of the cluster.

    This field is required for SCHEDULED billing to specify the reservation start
    time for the cluster. If not provided, the cluster provisions immediately.
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


class AcceptanceTestsParams(TypedDict, total=False):
    """
    AcceptanceTestsParams groups all GPU acceptance test options when enabled is true.
    """

    dcgm_diag_level: Literal[
        "DCGM_DIAG_LEVEL_SHORT", "DCGM_DIAG_LEVEL_MEDIUM", "DCGM_DIAG_LEVEL_LONG", "DCGM_DIAG_LEVEL_EXTENDED"
    ]
    """DCGM diagnostic depth.

    SHORT = readiness; MEDIUM = default; LONG = system validation; EXTENDED =
    memtest. An omitted value selects MEDIUM when enabled.
    """

    dcgm_diag_skipped: bool
    """Skip DCGM diagnostics acceptance test."""

    enabled: bool
    """Whether to run GPU acceptance tests during cluster bring-up."""

    gpu_burn_duration: int
    """GPU burn duration in seconds; 0 means use the default when enabled."""

    gpu_burn_skipped: bool
    """Skip GPU burn acceptance test."""

    nccl_multi_node_skipped: bool
    """Skip NCCL multi-node acceptance test."""

    nccl_single_node_skipped: bool
    """Skip NCCL single-node acceptance test."""

    storage_skipped: bool
    """Skip storage-performance acceptance test."""


class AddOnConfigDashboard(TypedDict, total=False):
    enabled: bool


class AddOnConfigIngress(TypedDict, total=False):
    enabled: bool


class AddOnConfig(TypedDict, total=False):
    dashboard: AddOnConfigDashboard

    ingress: AddOnConfigIngress


class AddOn(TypedDict, total=False):
    add_on_type: Required[str]
    """Type of add-on. Valid values: 'dashboard', 'ingress'."""

    name: Required[str]
    """Human-readable name for this add-on instance."""

    config: AddOnConfig


class ClusterConfigIngress(TypedDict, total=False):
    enabled: bool


class ClusterConfigObservability(TypedDict, total=False):
    enabled: bool


class ClusterConfigSlurmStartupScripts(TypedDict, total=False):
    """
    SlurmStartupScripts carries optional Slurm lifecycle scripts (prolog/epilog, init, extra conf).
    """

    controller_epilog: str
    """Slurm controller epilog script."""

    controller_prolog: str
    """Slurm controller prolog script."""

    extra_slurm_conf: str
    """Additional slurm.conf fragments."""

    login_init_script: str
    """Script run on Slurm login node init."""

    nodeset_init_script: str
    """Script run on Slurm nodeset init."""

    worker_epilog: str
    """Slurm worker node epilog script."""

    worker_prolog: str
    """Slurm worker node prolog script."""


class ClusterConfig(TypedDict, total=False):
    load_balancer: Required[Literal["NONE", "TRAEFIK", "NGINX", "ISTIO"]]

    gpu_operator_version: str
    """NVIDIA GPU Operator chart/version for the tenant cluster (e.g.

    v24.6.2). When omitted, a service default is applied.
    """

    ingress: ClusterConfigIngress

    jumphost_enabled: bool

    kubernetes_dashboard_enabled: bool

    network_operator_version: str
    """NVIDIA Network Operator chart/version for the tenant cluster (e.g.

    v24.7.0). When omitted, a service default is applied.
    """

    observability: ClusterConfigObservability

    slurm_startup_scripts: ClusterConfigSlurmStartupScripts
    """
    SlurmStartupScripts carries optional Slurm lifecycle scripts (prolog/epilog,
    init, extra conf).
    """


class OidcConfig(TypedDict, total=False):
    client_id: Required[str]
    """OIDC client ID for authentication."""

    group_claim: Required[str]
    """JWT claim to use for user groups. For example, 'groups'"""

    group_prefix: Required[str]
    """Prefix to add to the group claim to form the final group name.

    For example, 'oidc:'
    """

    issuer_url: Required[str]
    """OIDC issuer URL for authentication. For example, https://accounts.google.com"""

    username_claim: Required[str]
    """JWT claim to use as the username. For example, 'sub' or 'email'"""

    username_prefix: Required[str]
    """Prefix to add to the username claim to form the final username.

    For example, 'oidc:'
    """

    ca_cert: str
    """CA certificate in PEM format to validate the OIDC issuer's TLS certificate.

    This field is optional but recommended if the issuer uses a private CA or
    self-signed certificate.
    """


class SharedVolume(TypedDict, total=False):
    """Inline configuration to create a shared volume with the cluster creation."""

    region: Required[str]
    """Region name. Usable regions can be found from `clusters.list_regions()`"""

    size_tib: Required[int]
    """Volume size in whole tebibytes (TiB)."""

    volume_name: Required[str]
    """User provided name of the volume."""

    is_lifecycle_independent: bool
    """When true, the shared volume is not deleted when the cluster is decommissioned."""
