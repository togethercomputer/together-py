from __future__ import annotations

from datetime import datetime
from typing import Annotated

from cyclopts import Parameter
from rich import print as rprint
from rich.json import JSON

from together import AsyncTogether
from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import generate_progress_bar
from together.lib.utils.serializer import datetime_serializer


async def retrieve(
    fine_tune_id: str,
    json_output: bool = False,
    *,
    client: Annotated[AsyncTogether, Parameter(parse=False)],
) -> None:
    """Retrieve fine-tuning job details."""
    response = await client.fine_tuning.retrieve(fine_tune_id)
    if json_output:
        print(openapi_dumps(response.model_dump(exclude_none=True)))
        return
    response.events = None
    rprint(JSON.from_data(response.model_dump(exclude_none=True), default=datetime_serializer))
    progress_text = generate_progress_bar(response, datetime.now().astimezone(), use_rich=True)
    rprint(f"Status: [bold]{response.status}[/bold], {progress_text}")
