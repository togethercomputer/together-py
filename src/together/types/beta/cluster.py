# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from .clusters.remediation import Remediation

__all__ = [
    "Cluster",
    "AddOn",
    "AddOnConfig",
    "AddOnConfigDashboard",
    "AddOnConfigIngress",
    "AddOnState",
    "AddOnStateDashboard",
    "AddOnStateIngress",
    "ControlPlaneNode",
    "ControlPlaneNodePhaseTransition",
    "GPUWorkerNode",
    "GPUWorkerNodePhaseTransition",
    "PhaseTransition",
    "Volume",
    "ClusterConfig",
    "ClusterConfigIngress",
    "ClusterConfigObservability",
    "ClusterConfigSlurmStartupScripts",
    "OidcConfig",
]


class AddOnConfigDashboard(BaseModel):
    enabled: Optional[bool] = None


class AddOnConfigIngress(BaseModel):
    enabled: Optional[bool] = None


class AddOnConfig(BaseModel):
    dashboard: Optional[AddOnConfigDashboard] = None

    ingress: Optional[AddOnConfigIngress] = None


class AddOnStateDashboard(BaseModel):
    pass


class AddOnStateIngress(BaseModel):
    pass


class AddOnState(BaseModel):
    dashboard: Optional[AddOnStateDashboard] = None

    ingress: Optional[AddOnStateIngress] = None


class AddOn(BaseModel):
    """AddOnInfo is returned in cluster responses and add-on CRUD operations."""

    add_on_type: str

    config: AddOnConfig

    name: str

    state: AddOnState


class ControlPlaneNodePhaseTransition(BaseModel):
    phase: Literal[
        "NODE_PHASE_PENDING",
        "NODE_PHASE_SCHEDULING",
        "NODE_PHASE_BOOTING",
        "NODE_PHASE_BOOTSTRAPPING",
        "NODE_PHASE_RUNNING",
        "NODE_PHASE_SUCCEEDED",
        "NODE_PHASE_FAILED",
        "NODE_PHASE_PAUSED",
    ]
    """Node phase."""

    transition_time: datetime
    """Timestamp when the phase transition occurred."""


class ControlPlaneNode(BaseModel):
    host_name: str

    memory_gib: float

    network: str

    node_id: str

    num_cpu_cores: int

    phase_transitions: List[ControlPlaneNodePhaseTransition]
    """Phase transition history for this control plane node."""

    status: str

    public_ipv4: Optional[str] = None
    """Public IPv4 address of the control plane node."""


class GPUWorkerNodePhaseTransition(BaseModel):
    phase: Literal[
        "NODE_PHASE_PENDING",
        "NODE_PHASE_SCHEDULING",
        "NODE_PHASE_BOOTING",
        "NODE_PHASE_BOOTSTRAPPING",
        "NODE_PHASE_RUNNING",
        "NODE_PHASE_SUCCEEDED",
        "NODE_PHASE_FAILED",
        "NODE_PHASE_PAUSED",
    ]
    """Node phase."""

    transition_time: datetime
    """Timestamp when the phase transition occurred."""


class GPUWorkerNode(BaseModel):
    host_name: str

    memory_gib: float

    networks: List[str]

    node_id: str

    num_cpu_cores: int

    num_gpus: int

    phase_transitions: List[GPUWorkerNodePhaseTransition]
    """Phase transition history for this GPU worker node."""

    status: str

    auto_remediation_enabled: Optional[bool] = None
    """Whether auto-remediation is enabled for this node's instance."""

    ephemeral_storage: Optional[str] = None
    """Ephemeral storage size, such as 1Ti."""

    ib_hca_count: Optional[int] = None
    """Number of InfiniBand HCAs."""

    ib_hca_type: Optional[str] = None
    """InfiniBand HCA type."""

    instance_id: Optional[str] = None

    latest_remediation: Optional[Remediation] = None
    """
    Remediation represents a node remediation request for an instance. An instance
    can have multiple remediations over time (e.g., failed attempts followed by
    retries).
    """

    marked_for_deletion: Optional[bool] = None
    """Whether this node is marked for deletion by the operator."""

    nvswitch_count: Optional[int] = None
    """Number of NVSwitches."""

    nvswitch_type: Optional[str] = None
    """NVSwitch type."""

    public_ipv4: Optional[str] = None
    """Public IPv4 address of the GPU worker node."""

    slurm_worker_hostname: Optional[str] = None


class PhaseTransition(BaseModel):
    phase: Literal[
        "CLUSTER_PHASE_QUEUED",
        "CLUSTER_PHASE_SCHEDULED",
        "CLUSTER_PHASE_WAITING_FOR_CONTROL_PLANE_NODES",
        "CLUSTER_PHASE_WAITING_FOR_DATA_PLANE_NODES",
        "CLUSTER_PHASE_WAITING_FOR_SUBNET",
        "CLUSTER_PHASE_WAITING_FOR_SHARED_VOLUME",
        "CLUSTER_PHASE_WAITING_FOR_AUTO_SCALER",
        "CLUSTER_PHASE_INSTALLING_DRIVERS",
        "CLUSTER_PHASE_RUNNING_ACCEPTANCE_TESTS",
        "CLUSTER_PHASE_ACCEPTANCE_TESTS_FAILED",
        "CLUSTER_PHASE_RUNNING_NCCL_TESTS",
        "CLUSTER_PHASE_NCCL_TESTS_FAILED",
        "CLUSTER_PHASE_READY",
        "CLUSTER_PHASE_PAUSED",
        "CLUSTER_PHASE_ON_DEMAND_COMPUTE_PAUSED",
        "CLUSTER_PHASE_DEGRADED",
        "CLUSTER_PHASE_DELETING",
    ]
    """Cluster phase."""

    transition_time: datetime
    """Timestamp when the phase transition occurred."""


class Volume(BaseModel):
    size_tib: int
    """Size of the volume in TiB."""

    status: str
    """Current status of the volume."""

    volume_id: str
    """ID of the volume."""

    volume_name: str
    """User provided name of the volume."""


class ClusterConfigIngress(BaseModel):
    enabled: Optional[bool] = None


class ClusterConfigObservability(BaseModel):
    enabled: Optional[bool] = None


class ClusterConfigSlurmStartupScripts(BaseModel):
    """
    SlurmStartupScripts carries optional Slurm lifecycle scripts (prolog/epilog, init, extra conf).
    """

    controller_epilog: Optional[str] = None
    """Slurm controller epilog script."""

    controller_prolog: Optional[str] = None
    """Slurm controller prolog script."""

    extra_slurm_conf: Optional[str] = None
    """Additional slurm.conf fragments."""

    login_init_script: Optional[str] = None
    """Script run on Slurm login node init."""

    nodeset_init_script: Optional[str] = None
    """Script run on Slurm nodeset init."""

    worker_epilog: Optional[str] = None
    """Slurm worker node epilog script."""

    worker_prolog: Optional[str] = None
    """Slurm worker node prolog script."""


class ClusterConfig(BaseModel):
    load_balancer: Literal["NONE", "TRAEFIK", "NGINX", "ISTIO"]

    gpu_operator_version: Optional[str] = None
    """NVIDIA GPU Operator chart/version for the tenant cluster (e.g.

    v24.6.2). When omitted, a service default is applied.
    """

    ingress: Optional[ClusterConfigIngress] = None

    jumphost_enabled: Optional[bool] = None

    kubernetes_dashboard_enabled: Optional[bool] = None

    observability: Optional[ClusterConfigObservability] = None

    slurm_startup_scripts: Optional[ClusterConfigSlurmStartupScripts] = None
    """
    SlurmStartupScripts carries optional Slurm lifecycle scripts (prolog/epilog,
    init, extra conf).
    """


class OidcConfig(BaseModel):
    client_id: str
    """OIDC client ID for authentication."""

    group_claim: str
    """JWT claim to use for user groups. For example, 'groups'"""

    group_prefix: str
    """Prefix to add to the group claim to form the final group name.

    For example, 'oidc:'
    """

    issuer_url: str
    """OIDC issuer URL for authentication. For example, https://accounts.google.com"""

    username_claim: str
    """JWT claim to use as the username. For example, 'sub' or 'email'"""

    username_prefix: str
    """Prefix to add to the username claim to form the final username.

    For example, 'oidc:'
    """

    ca_cert: Optional[str] = None
    """CA certificate in PEM format to validate the OIDC issuer's TLS certificate.

    This field is optional but recommended if the issuer uses a private CA or
    self-signed certificate.
    """


class Cluster(BaseModel):
    add_ons: List[AddOn]
    """Enabled add-ons on this cluster.

    Only add-ons with enabled=true in their config are returned.
    """

    allocated_preemptible_gpus: int
    """Actual number of preemptible GPUs currently allocated to the cluster.

    Updated asynchronously by the fulfillment and reclamation workers; may be less
    than desired_preemptible_gpus when capacity is constrained.
    """

    billing_type: Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"]
    """Billing type for the cluster (RESERVED, ON_DEMAND, or SCHEDULED_CAPACITY)."""

    cluster_id: str

    cluster_name: str

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster."""

    control_plane_nodes: List[ControlPlaneNode]

    cuda_version: str

    desired_preemptible_gpus: int
    """Customer's requested number of preemptible GPUs.

    Set on cluster create or update; persists until changed.
    """

    gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"]

    gpu_worker_nodes: List[GPUWorkerNode]

    kube_config: str

    num_cpu_workers: int
    """Number of CPU-only worker nodes in the cluster."""

    num_gpus: int

    nvidia_driver_version: str

    phase_transitions: List[PhaseTransition]
    """Cluster-level phase transition history."""

    project_id: str

    region: str

    status: Literal[
        "WaitingForControlPlaneNodes",
        "WaitingForDataPlaneNodes",
        "WaitingForSubnet",
        "WaitingForSharedVolume",
        "InstallingDrivers",
        "RunningAcceptanceTests",
        "Paused",
        "OnDemandComputePaused",
        "Ready",
        "Degraded",
        "Deleting",
    ]
    """Current status of the GPU cluster."""

    volumes: List[Volume]

    capacity_pool_id: Optional[str] = None

    cluster_config: Optional[ClusterConfig] = None

    control_plane_ready: Optional[bool] = None
    """Whether the control plane is currently ready."""

    created_at: Optional[datetime] = None

    duration_hours: Optional[int] = None

    first_ready_at: Optional[datetime] = None
    """Timestamp when the cluster first reached the Ready phase."""

    install_traefik: Optional[bool] = None

    is_in_substrate: Optional[bool] = None
    """Whether the cluster is managed inside a substrate environment."""

    machine_cluster_id: Optional[str] = None
    """ID of the machine cluster backing this GPU cluster."""

    nvidia_driver_version_id: Optional[str] = None
    """Internal NVIDIA version ID for this cluster's driver and CUDA combination."""

    oidc_config: Optional[OidcConfig] = None

    os_image: Optional[str] = None
    """Data-volume image name for GPU worker nodes."""

    reservation_end_time: Optional[datetime] = None

    reservation_start_time: Optional[datetime] = None

    slurm_shm_size_gib: Optional[int] = None

    ums_org_id: Optional[str] = None
    """UMS organization ID associated with this cluster."""

    ums_project_id: Optional[str] = None
    """UMS project ID associated with this cluster."""
