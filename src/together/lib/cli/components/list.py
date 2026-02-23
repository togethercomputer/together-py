from __future__ import annotations

from typing import Any, Literal

from rich.box import ROUNDED
from rich.table import Table
from rich.console import Console, RenderResult, ConsoleOptions


class ListTable:
    def __init__(self, title: str | None = None):
        self.has_primary_column = False
        self.table = Table(
            box=ROUNDED,
            title=f"\n{title}" if title else None,
            title_style="primary",
            title_justify="left",
            header_style="table.header",
            border_style="table.border",
            padding=(0, 2),
            expand=True,
            show_lines=True,
        )

    def add_primary_column(
        self, name: str, *, ratio: int | None = None, justify: Literal["left", "center", "right"] = "left"
    ) -> None:
        self.has_primary_column = True
        self.table.add_column(name, ratio=ratio, justify=justify, style="primary")

    def add_column(
        self, name: str, *, ratio: int | None = 1, justify: Literal["left", "center", "right"] = "left"
    ) -> None:
        self.table.add_column(name, ratio=ratio, justify=justify, style="muted")

    def add_row(self, *values: Any) -> None:
        self.table.add_row(*values)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.has_primary_column is False:
            raise ValueError("No primary column added")
        yield self.table
