from __future__ import annotations

from typing import TypeVar, Awaitable

from together.lib.cli.utils._console import console

T = TypeVar("T")


async def show_loading_status(message: str, request: Awaitable[T]) -> T:
    with console.status(
        f"[progress.description]{message}[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",
    ):
        return await request
