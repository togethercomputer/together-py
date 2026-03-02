from __future__ import annotations

import getpass
import json as json_lib
from typing import Annotated, List, Literal, Optional

from cyclopts import Parameter
from rich import print as rprint

from together import AsyncTogether

from together.types.beta.cluster_create_params import ClusterCreateParams, SharedVolume


async def create(
    name: Optional[str] = None,
    num_gpus: Optional[int] = None,
    region: Optional[str] = None,
    billing_type: Optional[Literal["RESERVED", "ON_DEMAND"]] = None,
    driver_version: Optional[str] = None,
    duration_days: Optional[int] = None,
    gpu_type: Optional[str] = None,
    cluster_type: Optional[Literal["KUBERNETES", "SLURM"]] = None,
    volume: Optional[str] = None,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Create a cluster."""
    params: dict = dict(
        cluster_name=name,
        num_gpus=num_gpus,
        region=region,
        billing_type=billing_type,
        driver_version=driver_version,
        duration_days=duration_days,
        gpu_type=gpu_type,
        cluster_type=cluster_type,
    )
    if volume:
        params["volume_id"] = volume

    if not json_output:
        if not name:
            params["cluster_name"] = input(f"Clusters: Cluster name: [{getpass.getuser()}] ").strip() or getpass.getuser()
        if not gpu_type:
            params["gpu_type"] = input(
                "Clusters: Cluster GPU type (H100_SXM, H200_SXM, RTX_6000_PCI, L40_PCIE, B200_SXM, H100_SXM_INF): "
            ).strip()
        if not region:
            regions = await client.beta.clusters.list_regions()
            params["region"] = input(
                f"Clusters: Cluster region [{regions.regions[0].name}]: "
            ).strip() or regions.regions[0].name
        if num_gpus is None:
            n = input("Clusters: Cluster GPUs count (8-64): ").strip()
            params["num_gpus"] = int(n) if n else 8
        if not billing_type:
            params["billing_type"] = input("Clusters: Cluster billing type [ON_DEMAND]: ").strip() or "ON_DEMAND"
        if not driver_version:
            regions = await client.beta.clusters.list_regions()
            driver_versions: List[str] = []
            for r in regions.regions:
                if r.name == params.get("region"):
                    driver_versions.extend(r.driver_versions or [])
            params["driver_version"] = input(
                f"Clusters: Cluster driver version [CUDA_12_5_555]: "
            ).strip() or "CUDA_12_5_555"
        if duration_days is None and params.get("billing_type") == "RESERVED":
            d = input("Clusters: Cluster reserved duration (1-90 days) [3]: ").strip()
            params["duration_days"] = int(d) if d else 3
        if not cluster_type:
            params["cluster_type"] = input("Clusters: Cluster type [KUBERNETES]: ").strip() or "KUBERNETES"
        if not volume and "qa" not in str(client.base_url):
            if input("Clusters: Create a new storage volume? [y/N] ").strip().lower() in ("y", "yes"):
                default_volume_name = f"{params['cluster_name']}-storage"
                vol_name = input(f"Clusters: Storage volume name [{default_volume_name}]: ").strip() or default_volume_name
                size = input("Clusters: Storage volume size (TiB) [1]: ").strip()
                params["shared_volume"] = SharedVolume(
                    region=params["region"],
                    size_tib=int(size) if size else 1,
                    volume_name=vol_name,
                )
            else:
                volumes = await client.beta.clusters.storage.list()
                if volumes.volumes:
                    params["volume_id"] = input(
                        f"Clusters: Which storage volume to use? ({', '.join(v.volume_id for v in volumes.volumes)}): "
                    ).strip()
        print("Clusters: Creating cluster with the following parameters:", flush=True)
        rprint(ClusterCreateParams(**params))

    response = await client.beta.clusters.create(**params)
    if json_output:
        print(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        print("Clusters: Cluster created successfully")
        print(f"Clusters: {response.cluster_id}")
