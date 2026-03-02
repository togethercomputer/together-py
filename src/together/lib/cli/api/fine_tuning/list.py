from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import generate_progress_text
from together.lib.utils import finetune_price_to_dollars
from together.lib.utils.tools import format_datetime


status_colors = {
    "pending": "yellow",
    "queued": "yellow",
    "running": "yellow",
    "compressing": "yellow",
    "uploading": "yellow",
    "cancel_requested": "yellow",
    "cancelled": "red",
    "error": "red",
    "user_error": "red",
    "completed": "green",
}


async def list_(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List fine-tuning jobs."""
    response = await client.fine_tuning.list()
    response.data = response.data or []
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    if json_output:
        print(openapi_dumps(response.data))
        return

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        price = finetune_price_to_dollars(float(str(i.total_price)))
        status = str(i.status)
        if i.status == "running":
            status += f": {generate_progress_text(i, datetime.now(timezone.utc))}"
        display_list.append(
            {
                "ID": i.id,
                "Base Model": i.model or "",
                "Suffix": i.suffix or "",
                "Status": status,
                "Price": f"${price:,.2f}",
                "Created At": format_datetime(i.created_at),
            }
        )
    print(tabulate(display_list, headers="keys"))
