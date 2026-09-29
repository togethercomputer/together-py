"""JSON output mode for the CLI.

Humans stay on text unless they pass ``--json``. When ``detect_agent`` sees an
AI agent, JSON is the default so agents do not have to scrape styled text.
``--no-json`` forces text.
"""

from __future__ import annotations

import re
from typing import Any, Iterator, NoReturn
from contextlib import contextmanager
from collections.abc import Callable

from detect_agent import determine_agent

from together._utils._json import openapi_dumps
from together.lib.cli.utils._exit import CliDiagnosticExit
from together.lib.cli.utils._console import console

_MARKUP_RE = re.compile(r"\[/?[^\]]+\]")

# Set by the launcher for the current process/task. Library helpers that exit
# the process (validation, missing keys) read this instead of threading
# ``config.json`` through every call.
_enabled = False
_emitted = False
PrintFn = Callable[..., Any]
_real_print: PrintFn | None = None


def agent_detected() -> bool:
    return bool(determine_agent()["is_agent"])


def resolve_output_json(explicit: bool | None) -> bool:
    """``None`` means the flag was omitted: on for agents, off otherwise."""
    if explicit is not None:
        return explicit
    return agent_detected()


def use_json_mode(enabled: bool) -> None:
    global _enabled, _emitted
    _enabled = enabled
    _emitted = False


def is_json_mode() -> bool:
    return _enabled


def json_was_emitted() -> bool:
    return _emitted


def plain_text(value: str) -> str:
    return _MARKUP_RE.sub("", value).strip()


def emit_json(data: object) -> None:
    """Write one JSON document to stdout, even while human prints are suppressed."""
    global _emitted
    text = openapi_dumps(data).decode("utf-8")
    if _real_print is None:
        console.print_json(text)
    else:
        current = console.print
        console.print = _real_print  # type: ignore[method-assign]
        try:
            console.print_json(text)
        finally:
            console.print = current  # type: ignore[method-assign]
    _emitted = True


def exit_with_message(human: str, *, error: str | None = None, diagnostic: str | None = None) -> NoReturn:
    """Print ``human`` for people, or ``{"error": ...}`` in JSON mode, then exit 1."""
    message = error if error is not None else plain_text(human)
    if is_json_mode():
        emit_json({"error": message})
    else:
        console.print(human)
    raise CliDiagnosticExit(diagnostic or message)


@contextmanager
def suppress_human_output() -> Iterator[None]:
    """Drop styled status lines so a later JSON document is the only stdout.

    ``console.print_json`` still writes. Rich implements it via ``Console.print``,
    so the JSON path is pointed back at the original printer.
    """
    global _real_print
    original_print = console.print
    original_print_json = console.print_json
    previous_real = _real_print
    _real_print = original_print

    def dropped(*_args: Any, **_kwargs: Any) -> None:
        return None

    def print_json_bypass(*args: Any, **kwargs: Any) -> None:
        global _emitted
        console.print = original_print  # type: ignore[method-assign]
        try:
            original_print_json(*args, **kwargs)
        finally:
            console.print = dropped  # type: ignore[method-assign]
        _emitted = True

    console.print = dropped  # type: ignore[method-assign]
    console.print_json = print_json_bypass  # type: ignore[method-assign]
    try:
        yield
    finally:
        console.print = original_print  # type: ignore[method-assign]
        console.print_json = original_print_json  # type: ignore[method-assign]
        _real_print = previous_real
