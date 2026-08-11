from __future__ import annotations

import os
import sys
from typing import Any, TextIO, Literal, cast

from rich.theme import Theme
from rich.console import Console

CliThemeName = Literal["light", "dark"]
StreamName = Literal["stdout", "stderr"]


class _EncodingSafeStream:
    """Proxy writes through the current stdio stream without encoding crashes."""

    def __init__(self, stream_name: StreamName) -> None:
        self._stream_name = stream_name

    @property
    def _stream(self) -> TextIO:
        return cast(TextIO, getattr(sys, self._stream_name))

    def write(self, text: str) -> int:
        stream = self._stream
        encoding = getattr(stream, "encoding", None)
        if encoding:
            try:
                text.encode(encoding)
            except UnicodeEncodeError:
                text = text.encode(encoding, errors="replace").decode(encoding)
        return stream.write(text)

    def flush(self) -> None:
        self._stream.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)


# Dark theme: tuned for dark terminal backgrounds (original Together CLI palette).
_DARK_STYLES = {
    # Text styles
    "primary": "#caaef5",  # Purple 300
    "secondary": "#caaef5",  # solid (no dim) so help body text stays readable
    "accent": "#ff68d4",  # Pink 500
    "muted": "#98a0b3",  # Grey 400
    # Semantic styles
    "success": "bold #0dce74",  # Green 400
    "info": "#64afff",  # Blue 500
    "warning": "bold #ff815d",  # Red 500
    "error": "bold #c63800",  # Red 700
    # UI elements
    "prompt": "#ba92ff",  # Purple 500
    "prompt.choices": "#caaef5",  # Purple 300
    "prompt.default": "#98a0b3",  # Grey 400
    # Table styles
    "table.header": "#414858",
    "table.border": "#626b84",  # Grey 600
    "table.row": "#c4c9d4",  # Grey 300
    # Progress/Loading
    "progress.description": "#caaef5",  # Purple 300
    "progress.percentage": "bold #caaef5",
    "bar.complete": "#ba92ff",  # Purple 500
    "bar.finished": "#0dce74",  # Green 400
    "bar.pulse": "#ff68d4",  # Pink 500
}

# Light theme: high-contrast on white. Body copy uses near-black; brand purple is
# reserved for accents and kept dark enough for AA+. `[dim]` / `[white]` markup
# resolves through the theme, so overrides fix help examples and pagination
# without touching every call site.
_LIGHT_STYLES = {
    # Text styles — body text intentionally near-black (purple mid-tones still wash out)
    "primary": "bold #4c1d95",  # Violet 900 (~11:1 on white)
    "secondary": "#111827",  # Grey 900 — types / secondary labels
    "accent": "#9d174d",  # Pink 800
    "muted": "#1f2937",  # Grey 800 — descriptions / supporting copy
    # Replace ANSI dim / bright-white (both fail on light backgrounds)
    "dim": "#1f2937",  # Grey 800
    "white": "#000000",
    # Semantic styles
    "success": "bold #065f46",  # Green 800
    "info": "#1e40af",  # Blue 800
    "warning": "bold #9a3412",  # Orange 800
    "error": "bold #991b1b",  # Red 800
    # UI elements
    "prompt": "#4c1d95",  # Violet 900
    "prompt.choices": "#4c1d95",
    "prompt.default": "#1f2937",
    # Table styles
    "table.header": "#000000",
    "table.border": "#6b7280",  # Grey 500
    "table.row": "#111827",  # Grey 900
    # Progress/Loading
    "progress.description": "#4c1d95",
    "progress.percentage": "bold #4c1d95",
    "bar.complete": "#5b21b6",  # Violet 800
    "bar.finished": "#065f46",
    "bar.pulse": "#9d174d",
}


def resolve_cli_theme(
    env: dict[str, str] | None = None,
) -> CliThemeName:
    """Pick light/dark CLI theme from env.

    Precedence:
    1. ``TG_THEME`` or ``TOGETHER_CLI_THEME`` = ``light`` | ``dark``
    2. ``COLORFGBG`` background index (``>= 7`` → light)
    3. Default ``dark`` (historical CLI default)
    """
    environ = os.environ if env is None else env

    for key in ("TG_THEME", "TOGETHER_CLI_THEME"):
        explicit = environ.get(key, "").strip().lower()
        if explicit in ("light", "dark"):
            return explicit  # type: ignore[return-value]

    colorfgbg = environ.get("COLORFGBG", "").strip()
    if colorfgbg:
        bg_part = colorfgbg.split(";")[-1].strip()
        try:
            bg = int(bg_part)
        except ValueError:
            pass
        else:
            # ANSI: 0 black … 7 white, 8–15 bright. Light terminals commonly use 7 or 15.
            return "light" if bg >= 7 else "dark"

    return "dark"


def build_theme(theme_name: CliThemeName | None = None) -> Theme:
    name = resolve_cli_theme() if theme_name is None else theme_name
    styles = _LIGHT_STYLES if name == "light" else _DARK_STYLES
    return Theme(styles)


def create_console(theme_name: CliThemeName | None = None, *, stderr: bool = False) -> Console:
    stream_name: StreamName = "stderr" if stderr else "stdout"
    stream = cast(TextIO, _EncodingSafeStream(stream_name))
    return Console(theme=build_theme(theme_name), highlight=False, file=stream, stderr=stderr)


cli_theme_name: CliThemeName = resolve_cli_theme()
console = create_console(cli_theme_name)
error_console = create_console(cli_theme_name, stderr=True)
