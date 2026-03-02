from __future__ import annotations

import asyncio
from typing import Any, TypeVar, Coroutine

from together.lib.cli.utils._console import console

T = TypeVar("T")


async def show_loading_status(message: str, request: Coroutine[Any, Any, T]) -> T:
    task = asyncio.create_task(request)
    with console.status(
        f"[progress.description]{message}[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",
    ):
        await task
    return task.result()
