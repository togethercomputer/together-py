from datetime import datetime, timezone

import click
from rich import print as rprint, print_json

from together import Together
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import handle_api_errors, generate_progress_bar


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
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    # remove events from response for cleaner output
    response.events = None

    print_json(openapi_dumps(response).decode("utf-8"))
    progress_text = generate_progress_bar(response, datetime.now(timezone.utc), use_rich=True)
    prefix = f"Status: [bold]{response.status}[/bold],"
    rprint(f"{prefix} {progress_text}")
