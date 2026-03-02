from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.cli.api.beta.clusters._util import print_clusters


async def delete(
    cluster_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Delete a cluster by ID."""
    import sys

    if json_output:
        response = await client.beta.clusters.delete(cluster_id=cluster_id)
        print(json_lib.dumps(response.model_dump(), indent=2))
        return
    cluster = await client.beta.clusters.retrieve(cluster_id=cluster_id)
    print_clusters([cluster])
    resp = input(f"Clusters: Are you sure you want to delete cluster {cluster.cluster_name}? [y/N] ").strip().lower()
    if resp != "y" and resp != "yes":
        return
    print("Clusters: Deleting cluster...", file=sys.stderr)
    await client.beta.clusters.delete(cluster_id=cluster_id)
    print(f"Clusters: Deleted cluster {cluster.cluster_name}", file=sys.stderr)
