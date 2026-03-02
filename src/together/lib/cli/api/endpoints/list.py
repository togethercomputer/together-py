from __future__ import annotations

import json as json_lib
from typing import Annotated, Literal, Optional

from cyclopts import Parameter

from together import AsyncTogether, omit

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.utils.serializer import datetime_serializer
from together.lib.cli.api.endpoints._utils import print_endpoint

@handle_endpoint_api_errors("Endpoints")
async def list_(
    json_output: bool = False,
    type: Optional[Literal["dedicated", "serverless"]] = None,
    mine: Optional[bool] = None,
    usage_type: Optional[Literal["on-demand", "reserved"]] = None,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List all inference endpoints (includes both dedicated and serverless endpoints)."""
    import sys

    endpoints = await client.endpoints.list(
        type=type or omit,
        usage_type=usage_type or omit,
        mine=mine if mine is not None else omit,
    )

    if json_output:
        print(
            json_lib.dumps(
                [endpoint.model_dump() for endpoint in endpoints.data],
                default=datetime_serializer,
                indent=2,
            )
        )
        return

    if not endpoints:
        print("No dedicated endpoints found", file=sys.stderr)
        return

    print("Endpoints:", file=sys.stderr)
    show_autoscaling = mine is True
    for endpoint in endpoints.data:
        print_endpoint(endpoint, show_autoscaling=show_autoscaling)
        print(file=sys.stderr)
