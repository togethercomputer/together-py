from __future__ import annotations

import os
from typing import Literal

from rich.theme import Theme
from rich.console import Console

CliThemeName = Literal["light", "dark"]

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

# Light theme: darker brand tones + solid dim/white overrides for white backgrounds.
# `[dim]` / `[white]` markup resolves through the theme, so overrides fix widespread help
# and pagination output without touching every call site.
_LIGHT_STYLES = {
    # Text styles
    "primary": "#6d28d9",  # Violet 700
    "secondary": "#5b21b6",  # Violet 800
    "accent": "#db2777",  # Pink 600
    "muted": "#4b5563",  # Grey 600
    # Replace ANSI dim / bright-white (both fail on light backgrounds)
    "dim": "#4b5563",  # Grey 600
    "white": "#111827",  # Grey 900
    # Semantic styles
    "success": "bold #047857",  # Green 700
    "info": "#1d4ed8",  # Blue 700
    "warning": "bold #c2410c",  # Orange 700
    "error": "bold #b91c1c",  # Red 700
    # UI elements
    "prompt": "#6d28d9",  # Violet 700
    "prompt.choices": "#6d28d9",
    "prompt.default": "#4b5563",
    # Table styles
    "table.header": "#111827",  # Grey 900
    "table.border": "#9ca3af",  # Grey 400
    "table.row": "#1f2937",  # Grey 800
    # Progress/Loading
    "progress.description": "#6d28d9",
    "progress.percentage": "bold #6d28d9",
    "bar.complete": "#7c3aed",  # Violet 600
    "bar.finished": "#047857",
    "bar.pulse": "#db2777",
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


def create_console(theme_name: CliThemeName | None = None) -> Console:
    return Console(theme=build_theme(theme_name), highlight=False)


cli_theme_name: CliThemeName = resolve_cli_theme()
custom_theme = build_theme(cli_theme_name)
console = create_console(cli_theme_name)
