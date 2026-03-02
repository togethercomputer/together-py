from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List

from tabulate import tabulate

from cyclopts import Parameter

from together import AsyncTogether
from together._utils._json import openapi_dumps

from together.lib.utils.tools import format_timestamp
from together.lib.utils import convert_bytes, convert_unix_timestamp


async def list_(
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """List files."""
    response = await client.files.list()
    response.data = response.data or []
    epoch_start = datetime.fromtimestamp(0, tz=timezone.utc)
    response.data.sort(key=lambda x: x.created_at or epoch_start, reverse=True)

    if json_output:
        print(openapi_dumps(response.data))
        return

    display_list: List[Dict[str, Any]] = []
    for i in response.data:
        display_list.append(
            {
                "ID": i.id,
                "File name": i.filename or "",
                "Size": convert_bytes(float(str(i.bytes))),
                "Created At": format_timestamp(convert_unix_timestamp(i.created_at or 0)),
            }
        )
    print(tabulate(display_list, headers="keys"))
