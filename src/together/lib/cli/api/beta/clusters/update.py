from __future__ import annotations

import json as json_lib
from typing import Annotated, Literal, Optional

from cyclopts import Parameter

from together import AsyncTogether, omit



async def update(
    cluster_id: str,
    num_gpus: Optional[int] = None,
    cluster_type: Optional[Literal["KUBERNETES", "SLURM"]] = None,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Update a cluster."""
    import sys

    if not json_output:
        print("Clusters: Updating cluster...", file=sys.stderr)
    await client.beta.clusters.update(
        cluster_id,
        num_gpus=num_gpus if num_gpus is not None else omit,
        cluster_type=cluster_type if cluster_type is not None else omit,
    )
    if json_output:
        cluster = await client.beta.clusters.retrieve(cluster_id)
        print(json_lib.dumps(cluster.model_dump(exclude_none=True), indent=4))
    else:
        print("Clusters: Done", file=sys.stderr)
