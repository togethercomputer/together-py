from __future__ import annotations

from typing import Literal, Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.beta.clusters._json_params import parse_json_array, parse_json_object


async def update(
    cluster_id: str,
    num_gpus: Annotated[Optional[int], Parameter(help="Number of GPUs to allocate in the cluster")] = None,
    cluster_type: Annotated[
        Optional[Literal["KUBERNETES", "SLURM"]], Parameter(help="Type of cluster to update")
    ] = None,
    add_ons: Annotated[
        Optional[str],
        Parameter(help="Add-ons to update as a JSON array, or @path to a JSON file"),
    ] = None,
    cluster_config: Annotated[
        Optional[str],
        Parameter(help="Cluster config as a JSON object, or @path to a JSON file"),
    ] = None,
    num_preemptible_gpus: Annotated[
        Optional[int],
        Parameter(help="Desired number of preemptible GPUs for the cluster"),
    ] = None,
    num_reserved_gpus: Annotated[
        Optional[int],
        Parameter(help="Desired number of reserved GPUs for the cluster"),
    ] = None,
    reservation_end_time: Annotated[
        Optional[str],
        Parameter(help="Timestamp at which the cluster should be decommissioned"),
    ] = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """Update a cluster."""

    await show_loading_status(
        "Updating cluster...",
        config.client.beta.clusters.update(
            cluster_id,
            add_ons=parse_json_array(add_ons, "--add-ons") if add_ons else omit,
            cluster_config=parse_json_object(cluster_config, "--cluster-config") if cluster_config else omit,
            num_gpus=num_gpus if num_gpus is not None else omit,
            cluster_type=cluster_type if cluster_type is not None else omit,
            num_preemptible_gpus=num_preemptible_gpus if num_preemptible_gpus is not None else omit,
            num_reserved_gpus=num_reserved_gpus if num_reserved_gpus is not None else omit,
            reservation_end_time=reservation_end_time or omit,
        ),
    )

    if config.json:
        cluster = await config.client.beta.clusters.retrieve(cluster_id)
        console.print_json(openapi_dumps(cluster).decode("utf-8"))
    else:
        console.print("Cluster updated successfully")
