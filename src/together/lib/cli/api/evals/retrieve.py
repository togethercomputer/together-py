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
def retrieve(ctx: click.Context, evaluation_id: str, json: bool) -> None:
    """Get details of a specific evaluation job"""

    client: Together = ctx.obj

    response = client.evals.retrieve(evaluation_id)

    if json:
        print_json(openapi_dumps(response.model_dump(exclude_none=True)).decode("utf-8"))
    else:
        print_dict(response.to_dict())


def print_dict(data: Any, indent: int = 0) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"{' ' * indent}[bold dim]{key}:[/bold dim]")
                print_dict(value, indent=indent+2)
            elif isinstance(value, list):
                print(f"{' ' * indent}[bold dim]{key}:[/bold dim]")
                for index, item in enumerate(value):
                    print(f"{' ' * indent}[bold dim][{index}]:[/bold dim]")
                    print_dict(item, indent=indent+2)
            else:
                print(f"{' ' * indent}[bold dim]{key}:[/bold dim] {value}")
    else:
        print(f"{' ' * indent}{data}")