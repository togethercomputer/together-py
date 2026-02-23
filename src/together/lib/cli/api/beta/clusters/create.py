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
    Optional[Literal["RESERVED", "ON_DEMAND"]], Parameter(help="Billing type to use for the cluster")
]
NvidiaDriverVersionParameter = Annotated[Optional[str], Parameter(help="Nvidia driver version to use for the cluster")]
CudaVersionParameter = Annotated[Optional[str], Parameter(help="CUDA version to use for the cluster")]
DurationDaysParameter = Annotated[
    Optional[int], Parameter(help="Duration in days to keep the cluster running for reserved clusters")
]
GpuTypeParameter = Annotated[
    Optional[str],
    Parameter(
        help="GPU type to use for the cluster. Find available gpu types for each region with the `list-regions` command."
    ),
]
ClusterTypeParameter = Annotated[Optional[Literal["KUBERNETES", "SLURM"]], Parameter(help="Cluster type")]
VolumeParameter = Annotated[Optional[str], Parameter(help="Storage volume ID to use for the cluster")]


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
