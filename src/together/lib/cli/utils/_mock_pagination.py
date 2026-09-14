from __future__ import annotations

from typing import List, TypeVar, Optional
from typing_extensions import Annotated

from cyclopts import Parameter

T = TypeVar("T")

AfterParameter = Annotated[Optional[str], Parameter(name="after", help="The cursor to start from")]


def mock_pagination(
    data: List[T], cursor_field: str = "id", cursor: str | None = None, page_size: int = 20
) -> tuple[List[T], str | None]:
    """
    Mock pagination for a list of items.

    Args:
        data: The list of items to paginate.
        cursor_field: The field to use as the cursor.
        cursor: The cursor to start from.
        page_size: The number of items to return per page.
    """
    index_of_start = (
        next((i for i, item in enumerate(data) if getattr(item, cursor_field) == cursor), 0) + 1 if cursor else 0
    )

    items_to_display = data[index_of_start : index_of_start + page_size]

    next_index = index_of_start + page_size - 1
    if next_index < len(data):
        next_cursor = getattr(data[next_index], cursor_field)
    else:
        next_cursor = None

    return items_to_display, next_cursor
