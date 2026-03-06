from __future__ import annotations
from typing import Literal, Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table
from rich.box import ROUNDED

class ListTable:
    def __init__(self):
        self.has_primary_column = False
        self.table = Table(
            box=ROUNDED,
            header_style="table.header",
            border_style="table.border",
            padding=(0, 2),
            expand=True,
            show_lines=True
        )

    def add_primary_column(self, name: str, *, ratio: int, justify: Literal["left", "center", "right"] = "left"):
        self.has_primary_column = True
        self.table.add_column(name, ratio=ratio, justify=justify, style="primary")

    def add_column(self, name: str, *, ratio: int | None = None, justify: Literal["left", "center", "right"] = "left"):
        self.table.add_column(name, ratio=ratio, justify=justify, style="muted")


    def add_row(self, *values: Any):
        self.table.add_row(*values)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.has_primary_column is False:
            raise ValueError("No primary column added")
        yield self.table