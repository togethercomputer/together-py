from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether



async def retrieve(
    id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Retrieve file metadata."""
    response = await client.files.retrieve(id=id)
    print(json.dumps(response.model_dump(exclude_none=True), indent=4))
