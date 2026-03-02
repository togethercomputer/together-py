"""Endpoint-specific CLI utilities (e.g. error handling)."""

from __future__ import annotations

import sys
from typing import Any, TypeVar, Callable
from functools import wraps

from rich import print

from together import APIError
from together.types import DedicatedEndpoint
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils._console import console

F = TypeVar("F", bound=Callable[..., Any])


def handle_endpoint_api_errors(prefix: str) -> Callable[[F], F]:
    """Decorator to handle endpoint-specific API errors."""

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except APIError as e:
                error_msg = ""
                if e.body is not None:
                    error_msg = getattr(e.body, "message", str(e.body))
                else:
                    error_msg = str(e)
                error_lower = error_msg.lower()

                if "not found" in error_lower and "endpoint" in error_lower:
                    endpoint_id = kwargs.get("endpoint_id", "")
                    endpoint_display = f"'{endpoint_id}'" if endpoint_id else ""
                    print(f"{prefix}: Failed", file=sys.stderr)
                    print(f"{prefix}: Endpoint {endpoint_display} not found.", file=sys.stderr)
                    print(f"{prefix}: The endpoint may have been deleted or the ID may be incorrect.", file=sys.stderr)
                    print(f"{prefix}: Use 'together endpoints list' to see your endpoints.", file=sys.stderr)
                    sys.exit(1)
                if "permission" in error_lower or "forbidden" in error_lower or "unauthorized" in error_lower:
                    print(f"{prefix}: Failed", file=sys.stderr)
                    print(f"{prefix}: You don't have permission to access this resource.", file=sys.stderr)
                    print(f"{prefix}: This may belong to another user or organization.", file=sys.stderr)
                    sys.exit(1)
                if "credentials" in error_lower or "authentication" in error_lower:
                    print(f"{prefix}: Failed", file=sys.stderr)
                    print(f"{prefix}: Invalid API key or authentication failed.", file=sys.stderr)
                    sys.exit(1)
                raise e

        return wrapper  # type: ignore

    return decorator  # type: ignore


def print_endpoint(endpoint: DedicatedEndpoint, show_autoscaling: bool = True) -> None:
    """Print endpoint details in a Docker-like format or JSON."""
    console.print(f"[dim][primary]Name:[/primary][/dim]\t\t[bold]{endpoint.name}[/bold]")
    console.print(
        f"[dim][primary]ID:[/primary][/dim]\t\t[link={f'https://api.together.ai/endpoints/{endpoint.name}'}][white]{endpoint.id}[/white][/link]"
    )
    console.print(f"[dim][primary]State:[/primary][/dim]\t\t{colorized_endpoint_state(endpoint)}")
    console.print(f"[dim][primary]Hardware:[/primary][/dim]\t{endpoint.hardware}")
    console.print(f"[dim][primary]Model:[/primary][/dim]\t\t{endpoint.model}")
    if show_autoscaling:
        console.print(
            f"[dim][primary]Replicas:[/primary][/dim]\tmin: {endpoint.autoscaling.min_replicas}\n\t\tmax: {endpoint.autoscaling.max_replicas}"
        )

    console.print(f"[dim][primary]Created:[/primary][/dim]\t{format_datetime(endpoint.created_at)}")


def colorized_endpoint_state(endpoint: DedicatedEndpoint) -> str:
    state_colors = {
        "PENDING": "yellow",
        "STARTING": "yellow",
        "STARTED": "green",
        "STOPPING": "yellow",
        "STOPPED": "yellow",
        "ERROR": "red",
    }
    color = state_colors[endpoint.state] if endpoint.state in state_colors else "white"
    return f"[{color}]{endpoint.state.capitalize()}[/{color}]"
