from __future__ import annotations

import json as json_lib
import sys
from typing import Annotated

from cyclopts import Parameter

import asyncio

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.utils.serializer import datetime_serializer


@handle_endpoint_api_errors("Endpoints")
async def start(
    endpoint_id: str,
    wait: bool = False,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Start a dedicated inference endpoint."""
    response = await client.endpoints.update(endpoint_id, state="STARTED")

    if json_output:
        print(json_lib.dumps(response.model_dump(), default=datetime_serializer, indent=2))
        return

    print("Successfully marked endpoint as starting", file=sys.stderr)
    if wait:
        print("Waiting for endpoint to start...", file=sys.stderr)
        while (await client.endpoints.retrieve(endpoint_id)).state != "STARTED":
            await asyncio.sleep(1)
        print("Endpoint started", file=sys.stderr)
    print(endpoint_id)
