from typing import Any, Dict, List

import click
from rich import print_json
from tabulate import tabulate

from together import Together
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Fine-tuning")
@auto_track_command
def list_checkpoints(ctx: click.Context, fine_tune_id: str, json: bool) -> None:
    """List available checkpoints for a fine-tuning job"""
    client: Together = ctx.obj

    checkpoints = client.fine_tuning.list_checkpoints(fine_tune_id)
    checkpoints.data = checkpoints.data or []

    if json:
        print_json(openapi_dumps(checkpoints.data).decode("utf-8"))
        return

    display_list: List[Dict[str, Any]] = []
    for checkpoint in checkpoints.data:
        name = (
            f"{fine_tune_id}:{checkpoint.step}"
            if "intermediate" in checkpoint.checkpoint_type.lower()
            else fine_tune_id
        )
        display_list.append(
            {
                "Type": checkpoint.checkpoint_type,
                "Timestamp": format_timestamp(checkpoint.created_at),
                "Name": name,
            }
        )

    if display_list:
        click.echo(f"Job {fine_tune_id} contains the following checkpoints:")
        table = tabulate(display_list, headers="keys", tablefmt="grid")
        click.echo(table)
        click.echo("\nTo download a checkpoint, use `together fine-tuning download`")
    else:
        click.echo(f"No checkpoints found for job {fine_tune_id}")
