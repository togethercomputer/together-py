from __future__ import annotations

from typing import Any, Literal, Optional, Annotated

from cyclopts import Parameter
from rich.table import Table as RichTable

from together import omit
from together._utils._json import openapi_dumps
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable
from together.lib.cli.components.loader import show_loading_status
from together.lib.cli.utils._mock_pagination import AfterParameter, mock_pagination

PAGE_SIZE = 20


def _pricing_cell(model: Any) -> Any:
    """Rich table: dim labels in column 1, prices right-aligned in column 2."""
    see_pricing = f"[link=https://api.together.ai/models/{model.id}]see pricing[/link]"
    if not model.pricing or model.pricing.input <= 0 or model.pricing.output <= 0:
        return see_pricing
    t = RichTable(show_header=False, box=None, expand=True)
    t.add_column(style="dim", no_wrap=True, justify="right", ratio=2)
    t.add_column(justify="left", no_wrap=True, ratio=1)
    cached = model.pricing.cached_input
    t.add_row("input", f"${model.pricing.input:.2f}")
    if cached is not None and cached > 0:
        t.add_row("cached input", f"${cached:.2f}")
    t.add_row("output", f"${model.pricing.output:.2f}")
    return t


def _details_cell(model: Any) -> Any:
    """Rich table: dim labels in column 1, details right-aligned in column 2."""
    details = [
        f"[dim]modality:[/dim] {model.type or 'other'}",
    ]

    if model.context_length:
        details.append(f"[dim]context length:[/dim] {str(model.context_length)}")

    return "\n".join(details)


async def list(
    type: Annotated[
        Optional[Literal["dedicated"]],
        Parameter(name="--type", show_choices=True, help="Filter models by specified type"),
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
        console.print_json(openapi_dumps({"data": models_to_display, "next_cursor": next_cursor}).decode())
        return

    table = ListTable()
    table.add_primary_column("Model", ratio=3)
    table.add_column("Details")
    table.add_column("Pricing", justify="center")

    for model in models_to_display:
        details = _details_cell(model)
        pricing = _pricing_cell(model)

        table.add_row(
            f"[link=https://api.together.ai/models/{model.id}]{model.id}[/link]",
            details,
            pricing,
        )

    console.print(table)
    if next_cursor:
        console.print("\n[blue dim]To display the next page, run:[/blue dim]")
        console.print(f"  [dim]-[/dim] [white]tg models list --after {next_cursor}[/white]")
