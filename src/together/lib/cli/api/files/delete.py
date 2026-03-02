from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether



async def delete(
    id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Delete remote file."""
    response = await client.files.delete(id=id)
    print(json.dumps(response.model_dump(exclude_none=True), indent=4))
