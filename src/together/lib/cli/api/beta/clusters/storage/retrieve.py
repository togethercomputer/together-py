from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter
from rich import print as rprint

from together import AsyncTogether



async def retrieve(
    volume_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Retrieve a storage volume."""
    import sys

    if not json_output:
        print("Clusters Storage: Retrieving storage volume...", file=sys.stderr)
    response = await client.beta.clusters.storage.retrieve(volume_id)
    if json_output:
        print(json_lib.dumps(response.model_dump(), indent=2))
    else:
        rprint(response)
