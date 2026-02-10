"""Endpoint-specific CLI utilities (e.g. error handling)."""

from __future__ import annotations

import sys
from typing import Any, TypeVar, Callable
from functools import wraps

import click

from together import APIError

F = TypeVar("F", bound=Callable[..., Any])


def handle_endpoint_api_errors(prefix: str) -> Callable[[F], F]:
    """Decorator to handle endpoint-specific API errors. Must be used with handle_api_errors."""
    prefix_styled = click.style(f"{prefix}: ", fg="blue")

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
                    click.echo(prefix_styled + click.style("Failed", fg="red"))
                    click.echo(prefix_styled + click.style(f"Endpoint {endpoint_display} not found.", fg="red"))
                    click.echo(
                        prefix_styled + "The endpoint may have been deleted or the ID may be incorrect.",
                        err=True,
                    )
                    click.echo(
                        prefix_styled + "Use 'together endpoints list' to see your endpoints.",
                        err=True,
                    )
                    sys.exit(1)
                if "permission" in error_lower or "forbidden" in error_lower or "unauthorized" in error_lower:
                    click.echo(prefix_styled + click.style("Failed", fg="red"))
                    click.echo(
                        prefix_styled + click.style("You don't have permission to access this resource.", fg="red")
                    )
                    click.echo(
                        prefix_styled + "This may belong to another user or organization.",
                        err=True,
                    )
                    sys.exit(1)
                if "credentials" in error_lower or "authentication" in error_lower:
                    click.echo(prefix_styled + click.style("Failed", fg="red"))
                    click.echo(prefix_styled + click.style("Invalid API key or authentication failed.", fg="red"))
                    sys.exit(1)
                raise e

        return wrapper  # type: ignore

    return decorator  # type: ignore
