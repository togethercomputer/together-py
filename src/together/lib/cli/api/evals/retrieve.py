from __future__ import annotations

import json
from typing import Annotated

from cyclopts import Parameter

from together import AsyncTogether

from together.lib.utils.serializer import datetime_serializer


async def retrieve(
    evaluation_id: str,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Get details of a specific evaluation job."""
    response = await client.evals.retrieve(evaluation_id)
    print(json.dumps(response.model_dump(exclude_none=True), default=datetime_serializer, indent=4))
