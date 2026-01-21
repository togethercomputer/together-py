from __future__ import annotations

import json as json_lib
from typing import Literal

import click

from together import Together, omit
from together.lib.cli.api._utils import handle_api_errors


@click.command()
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
