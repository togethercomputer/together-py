from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether
from together.lib.cli.api.beta.clusters._util import print_clusters


async def list_(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List clusters."""
    response = await client.beta.clusters.list()
    if json_output:
        print(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        print_clusters(response.clusters)
