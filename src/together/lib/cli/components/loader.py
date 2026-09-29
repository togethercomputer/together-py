from __future__ import annotations

from typing import TypeVar, Iterator, Awaitable
from contextlib import contextmanager

from together.lib.cli.utils._debug import is_enabled, log_debug_note
from together.lib.cli.utils._console import console

T = TypeVar("T")


@contextmanager
def loading_status(message: str) -> Iterator[None]:
    """Show a spinner, or a debug line when ``--debug`` is on.

    Rich Live (stdout) and debug logs (stderr) share the terminal cursor, so a
    spinner would overwrite HTTP debug lines. Skip Live UI in debug mode.
    """
    if is_enabled():
        if message:
            log_debug_note(message)
        yield
        return
    with console.status(
        f"[progress.description]{message}[/progress.description]",
        spinner="dots",
        spinner_style="bar.pulse",
    ):
        yield


async def show_loading_status(message: str, request: Awaitable[T]) -> T:
    with loading_status(message):
        return await request
