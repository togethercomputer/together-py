from typing import Any, Dict, List
from textwrap import wrap

import click
from rich import print_json
from tabulate import tabulate

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Fine-tuning")
@auto_track_command
def list_events(ctx: click.Context, fine_tune_id: str, json: bool) -> None:
    """List fine-tuning events"""
    client: Together = ctx.obj

    response = client.fine_tuning.list_events(fine_tune_id)

    response.data = response.data or []

    if json:
        print_json(openapi_dumps(response.data).decode("utf-8"))
        return

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        display_list.append(
            {
                "Message": "\n".join(wrap(i.message or "", width=50)),
                "Type": i.type,
                "Created At": i.created_at,
                "Hash": i.hash,
            }
        )
    table = tabulate(display_list, headers="keys", tablefmt="grid", showindex=True)

    click.echo(table)
