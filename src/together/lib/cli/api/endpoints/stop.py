from __future__ import annotations

import json as json_lib
import sys
from typing import Annotated

from cyclopts import Parameter

import asyncio

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def stop(
    endpoint_id: str,
    wait: bool = False,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Stop a dedicated inference endpoint."""
    await client.endpoints.update(endpoint_id, state="STOPPED")

    if json_output:
        print(json_lib.dumps({"message": "Successfully marked endpoint as stopping"}, indent=2))
        return

    print("Successfully marked endpoint as stopping", file=sys.stderr)
    if wait:
        print("Waiting for endpoint to stop...", file=sys.stderr)
        while (await client.endpoints.retrieve(endpoint_id)).state != "STOPPED":
            await asyncio.sleep(1)
        print("Endpoint stopped", file=sys.stderr)
    print(endpoint_id)
