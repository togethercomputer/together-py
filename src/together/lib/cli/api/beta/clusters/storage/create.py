from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether



async def create(
    region: str,
    size_tib: int,
    volume_name: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Create a storage volume."""
    response = await client.beta.clusters.storage.create(
        region=region,
        size_tib=size_tib,
        volume_name=volume_name,
    )
    if json_output:
        print(json_lib.dumps(response.model_dump(), indent=2))
    else:
        print(response)
