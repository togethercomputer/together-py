from __future__ import annotations

import json as json_lib
import getpass
from typing import List, Literal

import click
from rich import print

from together import Together
from together.lib.cli.api._utils import handle_api_errors
from together.types.beta.cluster_create_params import SharedVolume, ClusterCreateParams


@click.command()
@click.option(
    "--name",
    type=str,
    help="Name of the cluster",
)
@click.option(
    "--num-gpus",
    type=int,
    help="Number of GPUs to allocate in the cluster",
)
@click.option(
    "--region",
    type=str,
    help="Region to create the cluster in",
)
@click.option(
    "--billing-type",
    type=str,
    help="Billing type to use for the cluster",
)
@click.option(
    "--driver-version",
    type=str,
    help="Driver version to use for the cluster",
)
@click.option(
    "--duration-days",
    type=int,
    help="Duration in days to keep the cluster running for reserved clusters",
)
@click.option(
    "--gpu-type",
    type=str,
    help="GPU type to use for the cluster. Find available gpu types for each region with the `list-regions` command.",
)
@click.option("--cluster-type", type=click.Choice(["KUBERNETES", "SLURM"]), help="Cluster type")
@click.option(
    "--volume",
    type=str,
    help="Storage volume ID to use for the cluster",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def create(
    ctx: click.Context,
    name: str | None = None,
    num_gpus: int | None = None,
    region: str | None = None,
    billing_type: Literal["RESERVED", "ON_DEMAND"] | None = None,
    driver_version: str | None = None,
    duration_days: int | None = None,
    gpu_type: str | None = None,
    cluster_type: Literal["KUBERNETES", "SLURM"] | None = None,
    volume: str | None = None,
    json: bool = False,
) -> None:
    """Create a cluster"""
    client: Together = ctx.obj

    params = ClusterCreateParams(
        cluster_name=name,  # type: ignore
        num_gpus=num_gpus,  # type: ignore
        region=region,  # type: ignore
        billing_type=billing_type,  # type: ignore
        driver_version=driver_version,  # type: ignore
        duration_days=duration_days,  # type: ignore
        gpu_type=gpu_type,  # type: ignore
        cluster_type=cluster_type,  # type: ignore
    )

    # Lazily add this so its not put in the object as None - just looks bad aesthetically
    if volume:
        params["volume_id"] = volume

    # JSON Mode skips hand holding through the argument setup
    if not json:
        if not name:
            params["cluster_name"] = click.prompt("Clusters: Cluster name:", default=getpass.getuser(), type=str)

        # TODO
        # GPU should be queried first
        # Validate region has the gpu selected.

        if not gpu_type:
            # TODO: Pull GPUS from region list and the region selected.
            # TODO: Add instance_types to region list api
            params["gpu_type"] = click.prompt(
                "Clusters: Cluster GPU type:",
                type=click.Choice(["H100_SXM", "H200_SXM", "RTX_6000_PCI", "L40_PCIE", "B200_SXM", "H100_SXM_INF"]),
            )

        if not region:
            regions = client.beta.clusters.list_regions()
            params["region"] = click.prompt(
                "Clusters: Cluster region:",
                default=regions.regions[0].name,
                type=click.Choice([region.name for region in regions.regions]),
            )

        if num_gpus is None:
            params["num_gpus"] = click.prompt("Clusters: Cluster GPUs count", type=click.IntRange(min=8, max=64))

        if not billing_type:
            params["billing_type"] = click.prompt(
                "Clusters: Cluster billing type:", default="ON_DEMAND", type=click.Choice(["RESERVED", "ON_DEMAND"])
            )

        if not driver_version:
            regions = client.beta.clusters.list_regions()

            # Get the driver versions for the selected region
            driver_versions: List[str] = []
            for region_obj in regions.regions:
                if region_obj.name == params["region"]:
                    driver_versions.extend(region_obj.driver_versions)

            params["driver_version"] = click.prompt(
                "Clusters: Cluster driver version:", default="CUDA_12_5_555", type=click.Choice(driver_versions)
            )

        if not duration_days and params["billing_type"] == "RESERVED":
            params["duration_days"] = click.prompt("Clusters: Cluster reserved duration (1-90 days):", default=3)

        if not cluster_type:
            params["cluster_type"] = click.prompt(
                "Clusters: Cluster type:", default="KUBERNETES", type=click.Choice(["KUBERNETES", "SLURM"])
            )

        # In our QA environment, we don't accept storage volume creation, so we skip the prompt
        if not volume and "qa" not in client.base_url.host:
            if click.confirm("Clusters: Create a new storage volume?"):
                default_volume_name = f"{params['cluster_name']}-storage"
                params["shared_volume"] = SharedVolume(
                    region=f"{params['region']}",
                    size_tib=1,
                    volume_name=default_volume_name,
                )
                params["shared_volume"]["volume_name"] = click.prompt(
                    "Clusters: Storage volume name:", default=default_volume_name, type=str
                )
                params["shared_volume"]["size_tib"] = click.prompt(
                    "Clusters: Storage volume size (TiB):", default=1, type=click.IntRange(min=1, max=1024)
                )
            else:
                # TODO: We need bound status and region on the volume list from the API.
                # Only show volumes in the region selected and that are not attached to a cluster.
                volumes = client.beta.clusters.storage.list()
                params["volume_id"] = click.prompt(
                    "Clusters: Which storage volume to use?",
                    default=volumes.volumes[0].volume_id,
                    type=click.Choice([volume.volume_id for volume in volumes.volumes]),
                )

        click.echo("Clusters: Creating cluster with the following parameters:")
        print(ClusterCreateParams(**params))  # type: ignore

    response = client.beta.clusters.create(**params)

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        click.echo(f"Clusters: Cluster created successfully")
        click.echo(f"Clusters: {response.cluster_id}")
