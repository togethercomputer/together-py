from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether



async def status(
    evaluation_id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Get the status and results of a specific evaluation job."""
    response = await client.evals.status(evaluation_id)
    print(json.dumps(response.model_dump(exclude_none=True), indent=4))
