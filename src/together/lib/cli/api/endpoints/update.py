from __future__ import annotations

import json as json_lib
import sys
from typing import Annotated, Any, Dict, Optional

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.cli.api.endpoints._utils import handle_endpoint_api_errors
from together.lib.utils.serializer import datetime_serializer


@handle_endpoint_api_errors("Endpoints")
async def update(
    endpoint_id: str,
    display_name: Optional[str] = None,
    min_replicas: Optional[int] = None,
    max_replicas: Optional[int] = None,
    inactive_timeout: Optional[int] = None,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Update a dedicated inference endpoint's configuration."""
    if not any([display_name, min_replicas, max_replicas, inactive_timeout is not None]):
        print("Error: At least one update option must be specified", file=sys.stderr)
        sys.exit(1)

    kwargs: Dict[str, Any] = {}
    if display_name is not None:
        kwargs["display_name"] = display_name
    if min_replicas is not None or max_replicas is not None:
        kwargs["autoscaling"] = {}
        if min_replicas is not None:
            kwargs["autoscaling"]["min_replicas"] = min_replicas
        if max_replicas is not None:
            kwargs["autoscaling"]["max_replicas"] = max_replicas
    if inactive_timeout is not None:
        kwargs["inactive_timeout"] = inactive_timeout

    response = await client.endpoints.update(endpoint_id, **kwargs)

    if json_output:
        print(json_lib.dumps(response.model_dump(), default=datetime_serializer, indent=2))
        return

    print("Updated endpoint configuration:", file=sys.stderr)
    if display_name:
        print(f"  Display name: {display_name}", file=sys.stderr)
    if min_replicas:
        print(f"  Min replicas: {min_replicas}", file=sys.stderr)
    if max_replicas:
        print(f"  Max replicas: {max_replicas}", file=sys.stderr)
    if inactive_timeout is not None:
        print(f"  Inactive timeout: {inactive_timeout} minutes", file=sys.stderr)
    print("Successfully updated endpoint", file=sys.stderr)
    print(endpoint_id)
