from __future__ import annotations

import getpass
from typing import Any, List, Literal, Optional, Annotated, cast

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.types.beta.cluster_create_params import SharedVolume, ClusterCreateParams

NameParameter = Annotated[Optional[str], Parameter(help="Name of the cluster")]
NumGpusParameter = Annotated[Optional[int], Parameter(help="Number of GPUs to allocate in the cluster")]
RegionParameter = Annotated[Optional[str], Parameter(help="Region to create the cluster in")]
BillingTypeParameter = Annotated[
    Optional[Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"]],
    Parameter(help="Billing type to use for the cluster"),
]
NvidiaDriverVersionParameter = Annotated[Optional[str], Parameter(help="Nvidia driver version to use for the cluster")]
CudaVersionParameter = Annotated[Optional[str], Parameter(help="CUDA version to use for the cluster")]
DurationDaysParameter = Annotated[
    Optional[int], Parameter(help="Duration in days to keep the cluster running for reserved clusters")
]
GpuTypeParameter = Annotated[
    Optional[str],
    Parameter(help="GPU type to use for the cluster (run `list-regions` to see available types per region)"),
]
ClusterTypeParameter = Annotated[Optional[Literal["KUBERNETES", "SLURM"]], Parameter(help="Cluster type")]
VolumeParameter = Annotated[Optional[str], Parameter(help="Storage volume ID to use for the cluster")]
AutoScaleParameter = Annotated[Optional[bool], Parameter(help="Enable cluster auto-scaling")]
AutoScaleMaxGpusParameter = Annotated[Optional[int], Parameter(help="Maximum GPUs for auto-scaling")]
CapacityPoolIDParameter = Annotated[Optional[str], Parameter(help="Capacity pool ID to use for the cluster")]
GpuNodeFailoverEnabledParameter = Annotated[
    Optional[bool], Parameter(help="Enable automated GPU node failover for the cluster")
]
InstallTraefikParameter = Annotated[Optional[bool], Parameter(help="Install Traefik ingress controller")]
NumCapacityPoolGpusParameter = Annotated[
    Optional[int], Parameter(help="Number of GPUs to allocate from a capacity pool")
]
NumPreemptibleGpusParameter = Annotated[Optional[int], Parameter(help="Number of preemptible GPUs to request")]
NumReservedGpusParameter = Annotated[Optional[int], Parameter(help="Number of prepaid reserved GPUs to request")]
ProjectIDParameter = Annotated[Optional[str], Parameter(help="Project ID for the cluster")]
ReservationEndTimeParameter = Annotated[Optional[str], Parameter(help="Reservation end time for scheduled capacity")]
ReservationStartTimeParameter = Annotated[
    Optional[str], Parameter(help="Reservation start time for scheduled capacity")
]
SlurmImageParameter = Annotated[Optional[str], Parameter(help="Custom Slurm image for Slurm clusters")]
SlurmShmSizeGibParameter = Annotated[Optional[int], Parameter(help="Shared memory size in GiB for Slurm clusters")]


async def create(
    name: NameParameter = None,
    num_gpus: NumGpusParameter = None,
    region: RegionParameter = None,
    billing_type: BillingTypeParameter = None,
    nvidia_driver_version: NvidiaDriverVersionParameter = None,
    cuda_version: CudaVersionParameter = None,
    duration_days: DurationDaysParameter = None,
    gpu_type: GpuTypeParameter = None,
    cluster_type: ClusterTypeParameter = None,
    volume: VolumeParameter = None,
    auto_scale: AutoScaleParameter = None,
    auto_scale_max_gpus: AutoScaleMaxGpusParameter = None,
    capacity_pool_id: CapacityPoolIDParameter = None,
    gpu_node_failover_enabled: GpuNodeFailoverEnabledParameter = None,
    install_traefik: InstallTraefikParameter = None,
    num_capacity_pool_gpus: NumCapacityPoolGpusParameter = None,
    num_preemptible_gpus: NumPreemptibleGpusParameter = None,
    num_reserved_gpus: NumReservedGpusParameter = None,
    project_id: ProjectIDParameter = None,
    reservation_end_time: ReservationEndTimeParameter = None,
    reservation_start_time: ReservationStartTimeParameter = None,
    slurm_image: SlurmImageParameter = None,
    slurm_shm_size_gib: SlurmShmSizeGibParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Create a cluster."""
    params: dict[str, Any] = dict(
        cluster_name=name,
        num_gpus=num_gpus,
        region=region,
        billing_type=billing_type,
        nvidia_driver_version=nvidia_driver_version,
        cuda_version=cuda_version,
        duration_days=duration_days,
        gpu_type=gpu_type,
        cluster_type=cluster_type,
    )
    if volume:
        params["volume_id"] = volume
    if auto_scale is not None:
        params["auto_scale"] = auto_scale
    if auto_scale_max_gpus is not None:
        params["auto_scale_max_gpus"] = auto_scale_max_gpus
    if capacity_pool_id:
        params["capacity_pool_id"] = capacity_pool_id
    if gpu_node_failover_enabled is not None:
        params["gpu_node_failover_enabled"] = gpu_node_failover_enabled
    if install_traefik is not None:
        params["install_traefik"] = install_traefik
    if num_capacity_pool_gpus is not None:
        params["num_capacity_pool_gpus"] = num_capacity_pool_gpus
    if num_preemptible_gpus is not None:
        params["num_preemptible_gpus"] = num_preemptible_gpus
    if num_reserved_gpus is not None:
        params["num_reserved_gpus"] = num_reserved_gpus
    if project_id:
        params["project_id"] = project_id
    if reservation_end_time:
        params["reservation_end_time"] = reservation_end_time
    if reservation_start_time:
        params["reservation_start_time"] = reservation_start_time
    if slurm_image:
        params["slurm_image"] = slurm_image
    if slurm_shm_size_gib is not None:
        params["slurm_shm_size_gib"] = slurm_shm_size_gib

    # JSON Mode skips hand holding through the argument setup
    if not config.json and not config.non_interactive:
        if not name:
            params["cluster_name"] = (
                input(f"Clusters: Cluster name: [{getpass.getuser()}] ").strip() or getpass.getuser()
            )
        if not gpu_type:
            params["gpu_type"] = input(
                "Clusters: Cluster GPU type (H100_SXM, H200_SXM, RTX_6000_PCI, L40_PCIE, B200_SXM, H100_SXM_INF): "
            ).strip()
        if not region:
            regions = await config.client.beta.clusters.list_regions()
            params["region"] = (
                input(f"Clusters: Cluster region [{regions.regions[0].name}]: ").strip() or regions.regions[0].name
            )
        if num_gpus is None:
            n = input("Clusters: Cluster GPUs count (8-64): ").strip()
            params["num_gpus"] = int(n) if n else 8
        if not billing_type:
            params["billing_type"] = input("Clusters: Cluster billing type [ON_DEMAND]: ").strip() or "ON_DEMAND"
        if not nvidia_driver_version:
            regions = await config.client.beta.clusters.list_regions()
            nvidia_driver_versions: List[str] = []
            for r in regions.regions:
                if r.name == params.get("region"):
                    for driver_version in r.driver_versions:
                        nvidia_driver_versions.append(driver_version.nvidia_driver_version)
            params["nvidia_driver_version"] = input(f"Clusters: Cluster Nvidia driver version [550]: ").strip() or "550"
        if not cuda_version:
            regions = await config.client.beta.clusters.list_regions()
            cuda_versions: List[str] = []
            for r in regions.regions:
                if r.name == params.get("region"):
                    for driver_version in r.driver_versions:
                        cuda_versions.append(driver_version.cuda_version)
            params["cuda_version"] = input(f"Clusters: Cluster CUDA version [12.5]: ").strip() or "12.5"
        if duration_days is None and params.get("billing_type") == "RESERVED":
            d = input("Clusters: Cluster reserved duration (1-90 days) [3]: ").strip()
            params["duration_days"] = int(d) if d else 3
        if not cluster_type:
            params["cluster_type"] = input("Clusters: Cluster type [KUBERNETES]: ").strip() or "KUBERNETES"
        if not volume and "qa" not in str(config.client.base_url):
            if input("Clusters: Create a new storage volume? [y/N] ").strip().lower() in ("y", "yes"):
                default_volume_name = f"{params['cluster_name']}-storage"
                vol_name = (
                    input(f"Clusters: Storage volume name [{default_volume_name}]: ").strip() or default_volume_name
                )
                size = input("Clusters: Storage volume size (TiB) [1]: ").strip()
                params["shared_volume"] = SharedVolume(
                    region=params["region"],
                    size_tib=int(size) if size else 1,
                    volume_name=vol_name,
                )
            else:
                volumes = await config.client.beta.clusters.storage.list()
                if volumes.volumes:
                    params["volume_id"] = input(
                        f"Clusters: Which storage volume to use? ({', '.join(v.volume_id for v in volumes.volumes)}): "
                    ).strip()
        console.print("Clusters: Creating cluster with the following parameters:")
        console.print(cast(ClusterCreateParams, params))

    response = await config.client.beta.clusters.create(**params)
    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
    else:
        console.print("Clusters: Cluster created successfully")
        console.print(f"Clusters: {response.cluster_id}")
