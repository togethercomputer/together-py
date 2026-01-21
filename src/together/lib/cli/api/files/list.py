from typing import Any, Dict, List
from textwrap import wrap

import click
from tabulate import tabulate

from together import Together
from together.lib.utils import convert_bytes, convert_unix_timestamp
from together.lib.cli.api._utils import handle_api_errors


@click.command()
@click.pass_context
@handle_api_errors("Files")
def list(ctx: click.Context) -> None:
    """List files"""
    client: Together = ctx.obj

    response = client.files.list()

    display_list: List[Dict[str, Any]] = []
    for i in response.data or []:
        display_list.append(
            {
                "File name": "\n".join(wrap(i.filename or "", width=30)),
                "File ID": i.id,
                "Size": convert_bytes(float(str(i.bytes))),  # convert to string for mypy typing
                "Created At": convert_unix_timestamp(i.created_at or 0),
                "Line Count": i.line_count,
            }
        )
    table = tabulate(display_list, headers="keys", tablefmt="grid", showindex=True)

    click.echo(table)
