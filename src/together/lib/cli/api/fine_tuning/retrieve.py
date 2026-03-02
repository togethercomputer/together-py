from __future__ import annotations

from typing import Annotated
from datetime import datetime

from rich import print, print_json
from cyclopts import Parameter

from together._utils._json import openapi_dumps
from together.lib.cli.api._utils import generate_progress_bar
from together.lib.cli.utils.config import CLIConfig


async def retrieve(
    fine_tune_id: str,
    *,
    config: Annotated[CLIConfig, Parameter(parse=False)],
) -> None:
    """Retrieve fine-tuning job details."""
    response = await config.client.fine_tuning.retrieve(fine_tune_id)

    if config.json:
        print_json(openapi_dumps(response).decode("utf-8"))
        return

    response.events = None
    progress_text = generate_progress_bar(response, datetime.now().astimezone(), use_rich=True)
    print(f"Status: [bold]{response.status}[/bold], {progress_text}")
