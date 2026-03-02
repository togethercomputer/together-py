from __future__ import annotations

from textwrap import wrap
from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether



async def list_events(
    fine_tune_id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List fine-tuning events."""
    response = await client.fine_tuning.list_events(fine_tune_id)
    response.data = response.data or []
    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        display_list.append(
            {
                "Message": "\n".join(wrap(i.message or "", width=50)),
                "Type": i.type,
                "Created At": i.created_at,
                "Hash": i.hash,
            }
        )
    print(tabulate(display_list, headers="keys", tablefmt="grid", showindex=True))
