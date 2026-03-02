from __future__ import annotations

import sys
from typing import Any, Dict, Optional, Annotated

from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfig
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.api.endpoints._utils import print_endpoint, handle_endpoint_api_errors


@handle_endpoint_api_errors("Endpoints")
async def update(
    endpoint_id: str,
    display_name: Optional[str] = None,
    min_replicas: Optional[int] = None,
    max_replicas: Optional[int] = None,
    inactive_timeout: Optional[int] = None,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Update a dedicated inference endpoint's configuration."""
    if not any([display_name, min_replicas, max_replicas, inactive_timeout is not None]):
        console.print("[red]Error:[/red] At least one update option must be specified")
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

    response = await show_loading_status("Updating endpoint...", config.client.endpoints.update(endpoint_id, **kwargs))

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print("[green]√[/green] Endpoint updated.")
    print_endpoint(response)
