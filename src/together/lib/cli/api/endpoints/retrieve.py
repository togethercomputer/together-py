from __future__ import annotations

import json as json_lib
from typing import Annotated, Callable

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.utils.serializer import datetime_serializer
from together.lib.cli.api.endpoints._utils import print_endpoint


@handle_endpoint_api_errors("Endpoints")
async def retrieve(
    endpoint_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Get a dedicated inference endpoint."""
    endpoint = await client.endpoints.retrieve(endpoint_id)
    if json_output:
        print(json_lib.dumps(endpoint.model_dump(), indent=2, default=datetime_serializer))
    else:
        print_endpoint(endpoint)
