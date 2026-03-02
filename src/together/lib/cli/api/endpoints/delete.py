from __future__ import annotations

import json as json_lib
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def delete(
    endpoint_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Delete a dedicated inference endpoint."""
    await client.endpoints.delete(endpoint_id)
    if json_output:
        print(json_lib.dumps({"message": "Successfully deleted endpoint"}, indent=2))
        return
    print("Successfully deleted endpoint", file=__import__("sys").stderr)
    print(endpoint_id)
