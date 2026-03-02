from __future__ import annotations

from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def availability_zones(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List all availability zones."""
    import sys

    avzones = await client.endpoints.list_avzones()
    if json_output:
        import json as json_lib

        print(json_lib.dumps(avzones.model_dump(), indent=2))
        return
    if not avzones or not avzones.avzones:
        print("No availability zones found", file=sys.stderr)
        return
    print("Available zones:", file=sys.stderr)
    for zone in sorted(avzones.avzones):
        print(f"  {zone}")
