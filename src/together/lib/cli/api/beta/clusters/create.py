from __future__ import annotations

import getpass
from typing import Any, Literal, Optional, Sequence, Annotated, cast

from cyclopts import Parameter

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.types.beta.cluster_create_params import AddOn, SharedVolume, ClusterCreateParams
from together.types.beta.cluster_list_regions_response import (
    RegionDriverVersion,
    ClusterListRegionsResponse,
)

KNOWN_GPU_TYPES = (
    "H100_SXM",
    "H200_SXM",
    "RTX_6000_PCI",
    "L40_PCIE",
    "B200_SXM",
    "H100_SXM_INF",
    "B300_SXM",
)

NameParameter = Annotated[Optional[str], Parameter(help="Name of the cluster")]
NumGpusParameter = Annotated[Optional[int], Parameter(help="Number of GPUs to allocate in the cluster")]
RegionParameter = Annotated[Optional[str], Parameter(help="Region to create the cluster in")]
BillingTypeParameter = Annotated[
    Optional[Literal["RESERVED", "ON_DEMAND", "SCHEDULED_CAPACITY"]],
    Parameter(help="Billing type to use for the cluster"),
]
NvidiaDriverVersionParameter = Annotated[Optional[str], Parameter(help="Nvidia driver version to use for the cluster")]
CudaVersionParameter = Annotated[Optional[str], Parameter(help="CUDA version to use for the cluster")]
OSParameter = Annotated[Optional[str], Parameter(help="Operating system for NVIDIA version selection")]
NvidiaVersionIDParameter = Annotated[
    Optional[str], Parameter(help="NVIDIA version catalog ID to use directly for the cluster")
]
DurationDaysParameter = Annotated[
    Optional[int], Parameter(help="Duration in days to keep the cluster running for reserved clusters")
]
GpuTypeParameter = Annotated[
    Optional[str],
    Parameter(
        help="GPU type to use for the cluster (run `list-regions` to see available types per region). "
        f"Known values include: {', '.join(KNOWN_GPU_TYPES)}"
    ),
]
ClusterTypeParameter = Annotated[Optional[Literal["KUBERNETES", "SLURM"]], Parameter(help="Cluster type")]
VolumeParameter = Annotated[Optional[str], Parameter(help="Storage volume ID to use for the cluster")]
AutoScaleParameter = Annotated[Optional[bool], Parameter(help="Enable cluster auto-scaling")]
AutoScaleMaxGpusParameter = Annotated[Optional[int], Parameter(help="Maximum GPUs for auto-scaling")]
CapacityPoolIDParameter = Annotated[Optional[str], Parameter(help="Capacity pool ID to use for the cluster")]
InstallTraefikParameter = Annotated[Optional[bool], Parameter(help="Install Traefik ingress controller")]
HeadlampParameter = Annotated[
    Optional[bool], Parameter(help="Enable the Headlamp Kubernetes dashboard add-on", negative=())
]
SlurmWebParameter = Annotated[Optional[bool], Parameter(help="Enable the Slurm Web add-on", negative=())]
NumCapacityPoolGpusParameter = Annotated[
    Optional[int], Parameter(help="Number of GPUs to allocate from a capacity pool")
]
NumPreemptibleGpusParameter = Annotated[Optional[int], Parameter(help="Number of preemptible GPUs to request")]
NumReservedGpusParameter = Annotated[Optional[int], Parameter(help="Number of prepaid reserved GPUs to request")]
ReservationEndTimeParameter = Annotated[Optional[str], Parameter(help="Reservation end time for scheduled capacity")]
ReservationStartTimeParameter = Annotated[
    Optional[str], Parameter(help="Reservation start time for scheduled capacity")
]
SlurmImageParameter = Annotated[Optional[str], Parameter(help="Custom Slurm image for Slurm clusters")]
SlurmShmSizeGibParameter = Annotated[Optional[int], Parameter(help="Shared memory size in GiB for Slurm clusters")]

_DEFAULT_NVIDIA_VERSION_CHOICE = 1


def _format_nvidia_version(version: RegionDriverVersion) -> str:
    return f"driver {version.nvidia_driver_version}, CUDA {version.cuda_version}, OS {version.os} ({version.id})"


def _region_nvidia_versions(
    catalog: ClusterListRegionsResponse,
    region: str,
) -> list[RegionDriverVersion]:
    for catalog_region in catalog.regions:
        if catalog_region.name == region:
            return catalog_region.driver_versions

    raise TogetherError(f"No NVIDIA versions are available in region '{region}'. Run `tg beta clusters list-regions`.")


def _resolve_nvidia_version(
    catalog: ClusterListRegionsResponse,
    *,
    region: str,
    nvidia_driver_version: str | None,
    cuda_version: str | None,
    os_name: str | None,
) -> RegionDriverVersion:
    matches = [
        version
        for version in _region_nvidia_versions(catalog, region)
        if (nvidia_driver_version is None or version.nvidia_driver_version == nvidia_driver_version)
        and (cuda_version is None or version.cuda_version == cuda_version)
        and (os_name is None or version.os == os_name)
    ]
    requested = ", ".join(
        value
        for value in (
            f"driver {nvidia_driver_version}" if nvidia_driver_version else "",
            f"CUDA {cuda_version}" if cuda_version else "",
            f"OS {os_name}" if os_name else "",
        )
        if value
    )

    if not matches:
        raise TogetherError(
            f"No NVIDIA version matches {requested} in region '{region}'. Run `tg beta clusters list-regions`."
        )
    if len(matches) > 1:
        choices = "; ".join(_format_nvidia_version(version) for version in matches)
        guidance = "Use --nvidia-version-id." if os_name else "Add --os or use --nvidia-version-id."
        raise TogetherError(
            f"Multiple NVIDIA versions match {requested} in region '{region}'. {guidance} Matches: {choices}"
        )

    return matches[0]


def _prompt_nvidia_version(versions: Sequence[RegionDriverVersion]) -> RegionDriverVersion:
    if not versions:
        raise TogetherError("No NVIDIA versions are available in the selected region.")

    console.print("Clusters: Available NVIDIA versions:")
    for choice, version in enumerate(versions, start=_DEFAULT_NVIDIA_VERSION_CHOICE):
        console.print(f"  {choice}. {_format_nvidia_version(version)}")

    raw_choice = input(f"Clusters: Select NVIDIA version [{_DEFAULT_NVIDIA_VERSION_CHOICE}]: ").strip()
    try:
        choice = int(raw_choice) if raw_choice else _DEFAULT_NVIDIA_VERSION_CHOICE
    except ValueError as exc:
        raise TogetherError("Select an NVIDIA version by its listed number.") from exc
    if choice < _DEFAULT_NVIDIA_VERSION_CHOICE or choice > len(versions):
        raise TogetherError(f"Select an NVIDIA version from 1 to {len(versions)}.")

    return versions[choice - _DEFAULT_NVIDIA_VERSION_CHOICE]


async def _set_nvidia_version_params(
    *,
    config: CLIConfigParameter,
    params: dict[str, Any],
    catalog: ClusterListRegionsResponse | None,
    interactive: bool,
    nvidia_version_id: str | None,
    nvidia_driver_version: str | None,
    cuda_version: str | None,
    os_name: str | None,
) -> None:
    semantic_version_given = any(value is not None for value in (nvidia_driver_version, cuda_version, os_name))
    if nvidia_version_id and semantic_version_given:
        raise TogetherError("Use either --nvidia-version-id or --nvidia-driver-version/--cuda-version/--os, not both.")

    has_driver = nvidia_driver_version is not None
    has_cuda = cuda_version is not None
    if not nvidia_version_id and (has_driver != has_cuda or (os_name is not None and not has_driver)):
        raise TogetherError("--nvidia-driver-version and --cuda-version must be provided together; --os requires both.")

    if nvidia_version_id:
        params["nvidia_version_id"] = nvidia_version_id
        params.pop("nvidia_driver_version", None)
        params.pop("cuda_version", None)
        return

    if not interactive and not has_driver:
        raise TogetherError(
            "Use --nvidia-version-id or provide --nvidia-driver-version and --cuda-version in non-interactive mode."
        )

    if has_driver and os_name is None:
        return

    region = params.get("region")
    if not region:
        raise TogetherError("--region is required when selecting an NVIDIA version.")

    if catalog is None:
        catalog = await config.client.beta.clusters.list_regions()
    if semantic_version_given:
        selected = _resolve_nvidia_version(
            catalog,
            region=region,
            nvidia_driver_version=nvidia_driver_version,
            cuda_version=cuda_version,
            os_name=os_name,
        )
    else:
        selected = _prompt_nvidia_version(_region_nvidia_versions(catalog, region))

    params["nvidia_version_id"] = selected.id
    params.pop("nvidia_driver_version", None)
    params.pop("cuda_version", None)


async def create(
    name: NameParameter = None,
    num_gpus: NumGpusParameter = None,
    region: RegionParameter = None,
    billing_type: BillingTypeParameter = None,
    nvidia_driver_version: NvidiaDriverVersionParameter = None,
    cuda_version: CudaVersionParameter = None,
    os: OSParameter = None,
    nvidia_version_id: NvidiaVersionIDParameter = None,
    duration_days: DurationDaysParameter = None,
    gpu_type: GpuTypeParameter = None,
    cluster_type: ClusterTypeParameter = None,
    volume: VolumeParameter = None,
    auto_scale: AutoScaleParameter = None,
    auto_scale_max_gpus: AutoScaleMaxGpusParameter = None,
    capacity_pool_id: CapacityPoolIDParameter = None,
    install_traefik: InstallTraefikParameter = None,
    headlamp_addon: HeadlampParameter = None,
    slurm_web_addon: SlurmWebParameter = None,
    num_capacity_pool_gpus: NumCapacityPoolGpusParameter = None,
    num_preemptible_gpus: NumPreemptibleGpusParameter = None,
    num_reserved_gpus: NumReservedGpusParameter = None,
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
    if install_traefik is not None:
        params["install_traefik"] = install_traefik
    add_ons: list[AddOn] = []
    if headlamp_addon is not None:
        add_ons.append(
            {
                "add_on_type": "headlamp",
                "name": "headlamp",
                "config": {"headlamp": {"enabled": headlamp_addon}},
            }
        )
    if slurm_web_addon is not None:
        add_ons.append(
            {
                "add_on_type": "slurm_web",
                "name": "slurm_web",
                "config": {"slurm_web": {"enabled": slurm_web_addon}},
            }
        )
    if add_ons:
        params["add_ons"] = add_ons
    if num_capacity_pool_gpus is not None:
        params["num_capacity_pool_gpus"] = num_capacity_pool_gpus
    if num_preemptible_gpus is not None:
        params["num_preemptible_gpus"] = num_preemptible_gpus
    if num_reserved_gpus is not None:
        params["num_reserved_gpus"] = num_reserved_gpus
    if config.project_id:
        params["project_id"] = config.project_id
    if reservation_end_time:
        params["reservation_end_time"] = reservation_end_time
    if reservation_start_time:
        params["reservation_start_time"] = reservation_start_time
    if slurm_image:
        params["slurm_image"] = slurm_image
    if slurm_shm_size_gib is not None:
        params["slurm_shm_size_gib"] = slurm_shm_size_gib

    # JSON Mode skips hand holding through the argument setup
    interactive = not config.json and not config.non_interactive
    catalog: ClusterListRegionsResponse | None = None
    if interactive:
        if not name:
            params["cluster_name"] = (
                input(f"Clusters: Cluster name: [{getpass.getuser()}] ").strip() or getpass.getuser()
            )
        if not gpu_type:
            params["gpu_type"] = input(f"Clusters: Cluster GPU type ({', '.join(KNOWN_GPU_TYPES)}): ").strip()
        if not region:
            catalog = await config.client.beta.clusters.list_regions()
            params["region"] = (
                input(f"Clusters: Cluster region [{catalog.regions[0].name}]: ").strip() or catalog.regions[0].name
            )
        if num_gpus is None:
            n = input("Clusters: Cluster GPUs count (8-64): ").strip()
            params["num_gpus"] = int(n) if n else 8
        if num_preemptible_gpus is None:
            n = input("Clusters: Cluster preemptible GPUs count [0]: ").strip()
            params["num_preemptible_gpus"] = int(n) if n else 0
        if not billing_type:
            params["billing_type"] = input("Clusters: Cluster billing type [ON_DEMAND]: ").strip() or "ON_DEMAND"

    await _set_nvidia_version_params(
        config=config,
        params=params,
        catalog=catalog,
        interactive=interactive,
        nvidia_version_id=nvidia_version_id,
        nvidia_driver_version=nvidia_driver_version,
        cuda_version=cuda_version,
        os_name=os,
    )

    if interactive:
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
