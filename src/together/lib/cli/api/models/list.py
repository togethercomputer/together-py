from __future__ import annotations

from typing import List, Literal, Optional, Annotated

from cyclopts import Parameter

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

PAGE_SIZE = 20


async def list(
    type: Annotated[
        Optional[Literal["dedicated"]],
        Parameter(name="--type", show_choices=True, help="Filter models by specified type."),
    ] = None,
    after: AfterParameter = None,
    *,
    config: CLIConfigParameter,
) -> None:
    """List models."""
    models_list = await show_loading_status(
        "Loading models...", config.client.models.list(dedicated=type == "dedicated" if type else omit)
    )

    models_to_display, next_cursor = mock_pagination(models_list, cursor_field="id", cursor=after)

    if config.json:
        console.print_json(openapi_dumps(models_to_display).decode())
        return

    table = ListTable()
    table.add_column("Modality")
    table.add_primary_column("Model", ratio=4)
    table.add_column("Context Length", justify="right")
    table.add_column("Pricing per 1M Tokens", justify="right")

    for model in models_to_display:
        price_parts: List[str] = []
        if model.pricing and model.pricing.input > 0 and model.pricing.output > 0:
            price_parts.append(f"${model.pricing.input:.2f}")
            price_parts.append(f"${model.pricing.output:.2f}")
        else:
            price_parts.append(f"[link=https://api.together.xyz/models/{model.id}]see pricing[/link]")
        table.add_row(
            model.type or "other",  # type: ignore
            f"[link=https://api.together.xyz/models/{model.id}]{model.id}[/link]",
            str(model.context_length) if model.context_length else "",
            " / ".join(price_parts),
        )

    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg models list --after {next_cursor}[/white]")
