from __future__ import annotations

import json as json_lib
from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether



async def list_regions(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List regions."""
    response = await client.beta.clusters.list_regions()
    if json_output:
        print(json_lib.dumps(response.model_dump(exclude_none=True), indent=4))
    else:
        data: List[Dict[str, Any]] = []
        for region in response.regions:
            data.append(
                {
                    "Name": region.name,
                    "Supported GPU Types": ", ".join(region.supported_instance_types or []),
                    "Driver Versions": ", ".join(region.driver_versions or []),
                }
            )
        print(tabulate(data, headers="keys", tablefmt="grid"))
