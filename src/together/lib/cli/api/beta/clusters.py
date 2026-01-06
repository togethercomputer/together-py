from __future__ import annotations

import json as json_lib
import getpass
from typing import Any, Dict, List, Literal

import click
from rich import print
from tabulate import tabulate

from together import Together, omit
from together._response import APIResponse as APIResponse
from together.types.beta import Cluster, ClusterCreateParams
from together.lib.cli.api.utils import handle_api_errors
from together.types.beta.cluster_create_params import SharedVolume
from together.lib.cli.api.beta.clusters_storage import storage


def print_clusters(clusters: List[Cluster]) -> None:
    data: List[Dict[str, Any]] = []
    for cluster in clusters:
        data.append(
            {
                "ID": cluster.cluster_id,
                "Name": cluster.cluster_name,
                "Status": cluster.status,
                "Region": cluster.region,
            }
        )
    click.echo(tabulate(data, headers="keys", tablefmt="grid"))


@click.group()
@click.pass_context
def clusters(ctx: click.Context) -> None:
    """Clusters API commands"""
    pass


clusters.add_command(storage)


@clusters.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
def list(ctx: click.Context, json: bool) -> None:
    """List clusters"""
    client: Together = ctx.obj

    response = client.beta.clusters.list()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        print_clusters(response.clusters)


@clusters.command()
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


@clusters.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def retrieve(ctx: click.Context, cluster_id: str, json: bool) -> None:
    """Retrieve a cluster by ID"""
    client: Together = ctx.obj

    if not json:
        click.echo(f"Clusters: Retrieving cluster...")

    response = client.beta.clusters.retrieve(cluster_id)

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        print(response)


@clusters.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--num-gpus",
    type=int,
    help="Number of GPUs to allocate in the cluster",
)
@click.option(
    "--cluster-type",
    type=click.Choice(["KUBERNETES", "SLURM"]),
    help="Cluster type",
)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def update(
    ctx: click.Context,
    cluster_id: str,
    num_gpus: int | None = None,
    cluster_type: Literal["KUBERNETES", "SLURM"] | None = None,
    json: bool = False,
) -> None:
    """Update a cluster"""
    client: Together = ctx.obj

    if not json:
        click.echo("Clusters: Updating cluster...")

    client.beta.clusters.update(
        cluster_id,
        num_gpus=num_gpus if num_gpus is not None else omit,
        cluster_type=cluster_type if cluster_type is not None else omit,
    )

    if json:
        cluster = client.beta.clusters.retrieve(cluster_id)
        click.echo(json_lib.dumps(cluster.model_dump(exclude_none=True), indent=4))
    else:
        click.echo("Clusters: Done")


@clusters.command()
@click.argument("cluster-id", required=True)
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def delete(ctx: click.Context, cluster_id: str, json: bool) -> None:
    """Delete a cluster by ID"""
    client: Together = ctx.obj

    if json:
        response = client.beta.clusters.delete(cluster_id=cluster_id)
        click.echo(json_lib.dumps(response.model_dump(), indent=2))
        return

    cluster = client.beta.clusters.retrieve(cluster_id=cluster_id)
    print_clusters([cluster])
    if not click.confirm(f"Clusters: Are you sure you want to delete cluster {cluster.cluster_name}?"):
        return

    click.echo("Clusters: Deleting cluster...")
    response = client.beta.clusters.delete(cluster_id=cluster_id)

    click.echo(f"Clusters: Deleted cluster {cluster.cluster_name}")


@clusters.command()
@click.option(
    "--json",
    is_flag=True,
    help="Output in JSON format",
)
@click.pass_context
@handle_api_errors("Clusters")
def list_regions(ctx: click.Context, json: bool) -> None:
    """List regions"""
    client: Together = ctx.obj

    response = client.beta.clusters.list_regions()

    if json:
        click.echo(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        data: List[Dict[str, Any]] = []
        for region in response.regions:
            data.append(
                {
                    "Name": region.name,
                    "Availability Zones": ", ".join(region.availability_zones) if region.availability_zones else "",
                    "Driver Versions": ", ".join(region.driver_versions) if region.driver_versions else "",
                }
            )
        click.echo(tabulate(data, headers="keys", tablefmt="grid"))
