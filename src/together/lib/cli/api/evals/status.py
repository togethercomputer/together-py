from __future__ import annotations

from typing import Any

import click
from rich import print, print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("evaluation_id", type=str, required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Evals")
def status(ctx: click.Context, evaluation_id: str, json: bool) -> None:
    """Get the status and results of a specific evaluation job"""

    client: Together = ctx.obj

    response = client.evals.status(evaluation_id)

    if json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return
    else:
        print(f"[bold dim]Status:[/bold dim] [green]{response.status}[/green]")
        print_dict(response.results.to_dict() if response.results else {})

def print_dict(data: dict[str, Any], indent: int = 0) -> None:
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{' ' * indent}[bold dim]{key}:[/bold dim]")
            print_dict(value, indent=indent+2)
        else:
            print(f"{' ' * indent}[bold dim]{key}:[/bold dim] {value}")
