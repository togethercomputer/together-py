from __future__ import annotations

from together.lib.cli.utils._console import console
from together.lib.cli.components.list import ListTable


def _render(t: ListTable, width: int = 80) -> str:
    with console.capture() as cap:
        console.print(t, width=width)
    return cap.get()


def test_list_table_empty_renders_panel_not_header_only_table() -> None:
    t = ListTable(title="Files", empty_message="Nothing to show")
    t.add_primary_column("ID")
    t.add_column("Name")
    out = _render(t, width=80)
    assert "Files" in out
    assert "Nothing to show" in out
    # Must not be a data table with column headers and no rows (header/body join).
    assert "├" not in out


def test_list_table_empty_no_title() -> None:
    t = ListTable()
    t.add_primary_column("A")
    out = _render(t, width=40)
    assert "Nothing to show" in out


def test_list_table_with_rows_still_table() -> None:
    t = ListTable(title="X")
    t.add_primary_column("ID")
    t.add_row("1")
    out = _render(t, width=40)
    assert "ID" in out
    assert "1" in out
    assert "Nothing to show" not in out
