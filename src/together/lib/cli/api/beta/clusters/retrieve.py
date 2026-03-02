from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter
from rich import print as rprint

from together import AsyncTogether



async def retrieve(
    cluster_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Retrieve a cluster by ID."""
    import sys

    if not json_output:
        print("Clusters: Retrieving cluster...", file=sys.stderr)
    response = await client.beta.clusters.retrieve(cluster_id)
    if json_output:
        print(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        rprint(response)
