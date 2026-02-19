from datetime import datetime

import click
from rich import print as rprint
from rich.json import JSON

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors, generate_progress_bar
from together.lib.utils.serializer import datetime_serializer


@click.command()
@click.pass_context
@click.argument("fine_tune_id", type=str, required=True)
@click.option("--json", is_flag=True, help="Output the response in JSON format")
@handle_api_errors("Fine-tuning")
def retrieve(ctx: click.Context, fine_tune_id: str, json: bool) -> None:
    """Retrieve fine-tuning job details"""
    client: Together = ctx.obj

    response = client.fine_tuning.retrieve(fine_tune_id)

    if json:
        click.echo(openapi_dumps(response.model_dump(exclude_none=True)))
        return

    # remove events from response for cleaner output
    response.events = None

    rprint(JSON.from_data(response.model_dump(exclude_none=True), default=datetime_serializer))
    progress_text = generate_progress_bar(response, datetime.now().astimezone(), use_rich=True)
    prefix = f"Status: [bold]{response.status}[/bold],"
    rprint(f"{prefix} {progress_text}")
