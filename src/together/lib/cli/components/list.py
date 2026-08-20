from __future__ import annotations

from typing import Any, Literal

from rich.box import ROUNDED, Box
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.console import Console, RenderResult, ConsoleOptions
from rich.padding import Padding


class ListTable:
    def __init__(
        self,
        title: str | None = None,
        *,
        empty_message: str | None = None,
        box: Box | None = ROUNDED,
        show_lines: bool = True,
        padding: tuple[int, int, int, int] | tuple[int, int] = (0, 2),
        width: int | None = None,
    ) -> None:
        self._title = title
        self._empty_message = empty_message
        self.has_primary_column = False
        self.table = Table(
            box=box,
            title=f"\n{title}" if title else None,
            title_style="primary",
            title_justify="left",
            header_style="table.header",
            border_style="table.border",
            padding=padding,
            expand=True,
            show_lines=show_lines,
            width=width,
        )

    def add_primary_column(
        self, name: str, *, ratio: int | None = None, justify: Literal["left", "center", "right"] = "left"
    ) -> None:
        self.has_primary_column = True
        self.table.add_column(name, ratio=ratio, justify=justify, style="primary")

    def add_column(
        self,
        name: str,
        *,
        ratio: int | None = 1,
        justify: Literal["left", "center", "right"] = "left",
        width: int | None = None,
        no_wrap: bool = False,
    ) -> None:
        self.table.add_column(name, ratio=ratio, justify=justify, style="muted", width=width, no_wrap=no_wrap)

    def add_row(self, *values: Any) -> None:
        self.table.add_row(*values)

    def _default_empty_message(self) -> str:
        return "Nothing to show"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.has_primary_column is False:
            raise ValueError("No primary column added")
        if self.table.row_count == 0:
            text = self._empty_message or self._default_empty_message()
            yield Panel(
                Align.left(Padding(text, (0, 1, 0, 1))),
                title=self._title,
                box=ROUNDED,
                title_align="left",
                border_style="table.border",
                expand=True,
            )
        else:
            yield self.table
