"""Endpoint-specific CLI utilities (e.g. error handling)."""

from __future__ import annotations

import sys
from typing import Any, TypeVar, Callable
from together.types import DedicatedEndpoint
from together.types.endpoint_list_response import Data as DedicatedEndpointListItem
from functools import wraps

from together import APIError

F = TypeVar("F", bound=Callable[..., Any])


def handle_endpoint_api_errors(prefix: str) -> Callable[[F], F]:
    """Decorator to handle endpoint-specific API errors. Must be used with handle_api_errors."""

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

def print_endpoint(endpoint: DedicatedEndpoint | DedicatedEndpointListItem, show_autoscaling: bool = True) -> None:
    """Print endpoint details in a Docker-like format or JSON."""
    import sys

    print(f"ID:\t\t{endpoint.id}", file=sys.stderr)
    print(f"Name:\t\t{endpoint.name}", file=sys.stderr)
    if isinstance(endpoint, DedicatedEndpoint):
        print(f"Display Name:\t{endpoint.display_name}", file=sys.stderr)
        print(f"Hardware:\t{endpoint.hardware}", file=sys.stderr)
        if show_autoscaling:
            print(f"Min Replicas:\t{endpoint.autoscaling.min_replicas}", file=sys.stderr)
            print(f"Max Replicas:\t{endpoint.autoscaling.max_replicas}", file=sys.stderr)
    elif getattr(endpoint, "type", None) == "dedicated":
        model_extra = getattr(endpoint, "model_extra", {})
        display_name = model_extra.get("display_name")
        if display_name:
            print(f"Display Name:\t{display_name}", file=sys.stderr)
        hw = model_extra.get("hardware")
        if hw:
            print(f"Hardware:\t{hw}", file=sys.stderr)
        if show_autoscaling:
            autoscaling = model_extra.get("autoscaling")
            if autoscaling:
                print(f"Min Replicas:\t{autoscaling.get('min_replicas', 'N/A')}", file=sys.stderr)
                print(f"Max Replicas:\t{autoscaling.get('max_replicas', 'N/A')}", file=sys.stderr)
    print(f"Model:\t\t{endpoint.model}", file=sys.stderr)
    print(f"Type:\t\t{endpoint.type}", file=sys.stderr)
    print(f"Owner:\t\t{endpoint.owner}", file=sys.stderr)
    print(f"State:\t\t{endpoint.state}", file=sys.stderr)
    print(f"Created:\t{endpoint.created_at}", file=sys.stderr)