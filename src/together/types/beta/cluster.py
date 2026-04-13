# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Cluster", "ControlPlaneNode", "GPUWorkerNode", "Volume"]


class ControlPlaneNode(BaseModel):
    host_name: str

    memory_gib: float

    network: str

    node_id: str

    node_name: str

    num_cpu_cores: int

    status: str


class GPUWorkerNode(BaseModel):
    host_name: str

    memory_gib: float

    networks: List[str]

    node_id: str

    node_name: str

    num_cpu_cores: int

    num_gpus: int

    status: str

    instance_id: Optional[str] = None


class Volume(BaseModel):
    size_tib: int

    status: str

    volume_id: str

    volume_name: str


class Cluster(BaseModel):
    cluster_id: str

    cluster_name: str

    cluster_type: Literal["KUBERNETES", "SLURM"]
    """Type of cluster."""

    control_plane_nodes: List[ControlPlaneNode]

    cuda_version: str

    gpu_type: Literal["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"]

    gpu_worker_nodes: List[GPUWorkerNode]

    kube_config: str

    num_gpus: int

    nvidia_driver_version: str

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

    created_at: Optional[datetime] = None

    duration_hours: Optional[int] = None

    install_traefik: Optional[bool] = None

    reservation_end_time: Optional[datetime] = None

    reservation_start_time: Optional[datetime] = None

    slurm_shm_size_gib: Optional[int] = None
