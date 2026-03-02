from __future__ import annotations

from typing import Literal, Optional, Annotated

from rich import print, print_json
from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.components.loader import show_loading_status


async def update(
    cluster_id: str,
    num_gpus: Optional[int] = None,
    cluster_type: Optional[Literal["KUBERNETES", "SLURM"]] = None,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Update a cluster."""

    # TODO: Figure out how to disable the loading status when json is true
    await show_loading_status(
        "Updating cluster...",
        config.client.beta.clusters.update(
            cluster_id,
            num_gpus=num_gpus if num_gpus is not None else omit,
            cluster_type=cluster_type if cluster_type is not None else omit,
        ),
    )

    if config.json:
        cluster = await config.client.beta.clusters.retrieve(cluster_id)
        print_json(openapi_dumps(cluster).decode("utf-8"))
    else:
        print("Cluster updated successfully")
