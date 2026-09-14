from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter
from rich.table import Table

from together import omit
from together.lib.utils import convert_bytes
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.loader import show_loading_status


async def list_files(
    id: Annotated[str, Parameter(help="Model or adapter ID (ml_...) whose files should be listed")],
    *,
    revision: Annotated[Optional[str], Parameter(help="Revision ID to filter files for")] = None,
    config: CLIConfigParameter,
) -> None:
    response = await show_loading_status(
        "Loading model files...", config.client.beta.models.list_files(id, revision_id=revision or omit)
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    console.print(f"[dim]Revision:[/dim] {response.revision_id}")
    console.print(f"[dim]Created: [/dim] {response.revision_created_at}")
    console.print(f"[dim]Total: [/dim] {response.total_size_bytes}")
    console.print()

    table = Table(show_lines=False, box=None, padding=(0, 4, 0, 0))
    table.add_column("Path", ratio=2)
    table.add_column("Size")
    table.add_column("Hash")
    for file in response.data or []:
        table.add_row(
            file.path or "",
            convert_bytes(float(str(file.size_bytes or 0))),
            _shorten_hash(file.hash or ""),
        )
    console.print(table)
    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(
            f"  [dim]-[/dim] [white]tg beta models ls-files {id} f{f'--revision {revision}' if revision else ''} --after {response.next_cursor}[/white]"
        )


def _shorten_hash(value: str) -> str:
    return value[:8] + "..." + value[-8:]
