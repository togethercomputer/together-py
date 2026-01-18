import json

import click

from together import Together
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.argument("evaluation_id", type=str, required=True)
@handle_api_errors("Evals")
def status(ctx: click.Context, evaluation_id: str) -> None:
    """Get the status and results of a specific evaluation job"""

    client: Together = ctx.obj

    response = client.evals.status(evaluation_id)

    click.echo(json.dumps(response.model_dump(exclude_none=True), indent=4))
