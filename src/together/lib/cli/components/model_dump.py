from __future__ import annotations

from typing import Any, cast
from datetime import datetime

from rich.table import Table

from together import BaseModel
from together.lib.utils.tools import format_datetime
from together.lib.cli.utils._console import console


def print_model_dump(model: BaseModel) -> None:
    console.print(_pretty_print_results(dump_sorted_model(model), expand=True))


def _pretty_print_results(results: Any, expand: bool = False) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 0), expand=expand)
    table.add_column("Key", style="dim")
    table.add_column("Value", justify="left")
    if isinstance(results, dict):
        for key, value in cast(dict[str, Any], results).items():
            if isinstance(value, dict) or isinstance(value, list):
                table.add_row(_humanize_key(key), _pretty_print_results(value))
            else:
                table.add_row(_humanize_key(key), _colorize_value(value))
    elif isinstance(results, list):
        for item in cast(list[Any], results):
            table.add_row("-", _pretty_print_results(item))
    elif isinstance(results, BaseModel):
        table.add_row("", _pretty_print_results(results.model_dump()))
    else:
        table.add_row("", _colorize_value(results))
    return table


def _humanize_key(key: str) -> str:
    return f"{key.replace('_', ' ').title()}:"


def _colorize_value(value: Any) -> str:
    if value is None:
        return "[dim italic]n/a[/dim italic]"
    if isinstance(value, bool):
        return "[bold green]True[/bold green]" if value else "[bold red]False[/bold red]"
    if isinstance(value, float):
        return f"[bold blue]{value:g}[/bold blue]"
    if isinstance(value, int):
        return f"[bold blue]{value:d}[/bold blue]"
    if isinstance(value, datetime):
        return f"[bold blue]{format_datetime(value)}[/bold blue]"

    value = str(value)
    value = value.replace("\n", "\\n")
    value = value.replace("\t", "\\t")

    return f"[bold blue]{value}[/bold blue]"


def dump_sorted_model(model: BaseModel) -> dict[str, Any]:
    """Returns a model dump where the properties are sorted by their type:
    - ID fields first
    - Primitives next
    - Dicts/objects next
    - Lists last
    """

    def _sort_items(key: str, value: Any) -> int:
        # Returns a sort key: 0 for ID fields, 1 for primitives, 2 for dicts/objects, 3 for lists
        if key.endswith("_id"):
            return 0
        elif isinstance(value, dict) or isinstance(value, BaseModel):
            return 2
        elif isinstance(value, list):
            return 3
        else:
            return 1

    return dict(sorted(model.model_dump().items(), key=lambda kv: _sort_items(kv[0], kv[1])))
