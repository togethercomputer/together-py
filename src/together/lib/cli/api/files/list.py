from typing import Any, Dict, List
from datetime import datetime, timezone

import click
from tabulate import tabulate

from together import Together
from together.lib.utils import convert_bytes, convert_unix_timestamp
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@click.option("--json", is_flag=True, help="Print output in JSON format")
@handle_api_errors("Files")
def list(ctx: click.Context, json: bool) -> None:
    """List files"""
    client: Together = ctx.obj

    response = client.files.list()

    response.data = response.data or []

    # Use a default datetime for None values to make sure the key function always returns a comparable value
    # Sort newest to oldest
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    if json:
        click.echo(openapi_dumps(response.data))
        return

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        display_list.append(
            {
                "ID": click.style(i.id, fg="blue"),
                "File name": click.style(i.filename or "", fg="blue"),
                "Size": click.style(convert_bytes(float(str(i.bytes))), fg="blue"),  # convert to string for mypy typing
                "Created At": click.style(format_timestamp(convert_unix_timestamp(i.created_at or 0)), fg="blue"),
            }
        )
    table = tabulate(display_list, headers="keys")

    click.echo(table)
