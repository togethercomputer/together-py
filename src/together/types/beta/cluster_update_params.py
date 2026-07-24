# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "ClusterUpdateParams",
    "AddOn",
    "AddOnConfig",
    "AddOnConfigDashboard",
    "AddOnConfigHeadlamp",
    "AddOnConfigIngress",
    "AddOnConfigSlurmWeb",
    "AddOnConfigTorchpass",
    "ClusterConfig",
    "ClusterConfigIngress",
    "ClusterConfigObservability",
    "ClusterConfigSlurmStartupScripts",
]


class ClusterUpdateParams(TypedDict, total=False):
    add_ons: Iterable[AddOn]
    """Add-ons to update on the cluster.

    Each entry identifies an existing add-on by name and provides the new external
    config to merge.
    """

    cluster_config: ClusterConfig

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster to update."""

    num_capacity_pool_gpus: int
    """Number of GPUs to draw from the cluster's capacity pool.

    Only valid for clusters created with a capacity_pool_id. Must be a multiple of 8
    and not exceed num_gpus. When omitted, the current value is preserved.
    """

    num_gpus: int
    """Target GPU count for the cluster.

    When omitted, the server keeps the current GPU count from cluster metadata (use
    for config-only or decommission-time-only updates).
    """

    num_preemptible_gpus: int
    """Updated desired number of preemptible GPUs for the cluster.

    When omitted, the current value is preserved. Must be a multiple of 8.
    """

    num_reserved_gpus: int
    """Number of reserved GPUs to update to.

    This field is only applicable for clusters with RESERVED billing type.
    """

    reservation_end_time: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Timestamp at which the cluster should be decommissioned.

    Only accepted for prepaid clusters.
    """


class AddOnConfigDashboard(TypedDict, total=False):
    enabled: bool


class AddOnConfigHeadlamp(TypedDict, total=False):
    """Configuration for the Headlamp Kubernetes dashboard add-on."""

    enabled: bool
    """Whether to enable the Headlamp Kubernetes dashboard add-on."""


class AddOnConfigIngress(TypedDict, total=False):
    enabled: bool


class AddOnConfigSlurmWeb(TypedDict, total=False):
    """Configuration for the Slurm Web add-on."""

    enabled: bool
    """Whether to enable the Slurm Web add-on."""


class AddOnConfigTorchpass(TypedDict, total=False):
    """Configuration for the Model Aware TorchPass add-on."""

    enabled: bool
    """Whether to enable the Model Aware TorchPass add-on."""


class AddOnConfig(TypedDict, total=False):
    """Configuration for a cluster add-on."""

    dashboard: AddOnConfigDashboard

    headlamp: AddOnConfigHeadlamp
    """Configuration for the Headlamp Kubernetes dashboard add-on."""

    ingress: AddOnConfigIngress

    slurm_web: AddOnConfigSlurmWeb
    """Configuration for the Slurm Web add-on."""

    torchpass: AddOnConfigTorchpass
    """Configuration for the Model Aware TorchPass add-on."""


class AddOn(TypedDict, total=False):
    name: Required[str]
    """Name of the add-on to update. Must match an existing add-on on the cluster."""

    config: AddOnConfig
    """Configuration for a cluster add-on."""


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

    ssh_ca_enabled: bool
    """
    Whether this cluster uses a per-cluster SSH certificate authority for
    OIDC-signed SSH access.
    """
