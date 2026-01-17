from typing import Any, Dict, List
from datetime import datetime, timezone
from textwrap import wrap

import click
from tabulate import tabulate

from together import Together
from together.lib.utils import finetune_price_to_dollars
from together.lib.cli.api._utils import handle_api_errors, generate_progress_bar


@click.command()
@click.pass_context
@handle_api_errors("Fine-tuning")
def list(ctx: click.Context) -> None:
    """List fine-tuning jobs"""
    client: Together = ctx.obj

    response = client.fine_tuning.list()

    response.data = response.data or []

    # Use a default datetime for None values to make sure the key function always returns a comparable value
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start)

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        display_list.append(
            {
                "Fine-tune ID": i.id,
                "Model Output Name": "\n".join(wrap(i.x_model_output_name or "", width=30)),
                "Status": i.status,
                "Created At": i.created_at,
                "Price": f"""${
                    finetune_price_to_dollars(float(str(i.total_price)))
                }""",  # convert to string for mypy typing
                "Progress": generate_progress_bar(i, datetime.now().astimezone(), use_rich=False),
            }
        )
    table = tabulate(display_list, headers="keys", tablefmt="grid", showindex=True)

    click.echo(table)
