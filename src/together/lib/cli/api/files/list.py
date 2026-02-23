from __future__ import annotations

from datetime import datetime, timezone

from together.lib.utils import convert_bytes, convert_unix_timestamp
from together._utils._json import openapi_dumps
from together.lib.utils.tools import format_timestamp
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination


async def list(
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List files."""
    response = await show_loading_status("Loading files...", config.client.files.list())
    response.data = response.data or []
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    files_to_display, next_cursor = mock_pagination(response.data, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(files_to_display).decode("utf-8"))
        return

    table = ListTable(title="Files")
    table.add_primary_column("ID")
    table.add_column("File name")
    table.add_column("Size")
    table.add_column("Created At")

    for i in files_to_display:
        table.add_row(
            i.id,
            i.filename or "",
            convert_bytes(float(str(i.bytes))),
            format_timestamp(convert_unix_timestamp(i.created_at or 0)),
        )
    console.print(table)
    if next_cursor:
        console.print(f"\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg files list --after {next_cursor}[/white]")
