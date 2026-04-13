import json

import click

from together import Together
from together.lib.cli._track_cli import auto_track_command
from together.lib.cli.api._utils import handle_api_errors
from together.lib.utils.serializer import datetime_serializer


@click.command()
@click.pass_context
@click.argument("evaluation_id", type=str, required=True)
@handle_api_errors("Evals")
@auto_track_command
def retrieve(ctx: click.Context, evaluation_id: str) -> None:
    """Get details of a specific evaluation job"""

    client: Together = ctx.obj

    response = client.evals.retrieve(evaluation_id)

    click.echo(json.dumps(response.model_dump(exclude_none=True), default=datetime_serializer, indent=4))
