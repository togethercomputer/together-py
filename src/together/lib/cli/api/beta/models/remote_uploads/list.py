from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter
from together.lib.cli.api.beta.models.remote_uploads._utils import format_status


async def list(
    *,
    limit: Annotated[Optional[int], Parameter(help="Maximum jobs to return")] = None,
    after: AfterParameter = None,
    config: CLIConfigParameter,
) -> None:
    """List remote upload jobs."""

    response = await show_loading_status(
        "Loading remote upload jobs...",
        config.client.beta.models.remote_uploads.list(
            limit=limit if limit is not None else omit,
            after=after or omit,
        ),
    )

    if config.json:
        console.print_json(openapi_dumps(response).decode("utf-8"))
        return

    table = ListTable(
        "Remote Uploads",
        empty_message=(
            "No remote upload jobs found. To start one run:\n"
            "  [dim]-[/dim] [primary]tg beta models remote-uploads create <model-id> --from <url>[/primary]"
        ),
    )
    table.add_primary_column("Job ID")
    table.add_column("Model", ratio=2)
    table.add_column("Status")
    for upload in response.data:
        table.add_row(
            upload.id or "",
            upload.api_model_id or "",
            format_status(upload.status),
        )
    console.print(table)

    if response.next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg beta models remote-uploads ls --after {response.next_cursor}[/white]")
