from __future__ import annotations

import io
import sys

import pytest
from rich.console import Console

from together.lib.cli.utils._console import (
    _DARK_STYLES,
    _LIGHT_STYLES,
    build_theme,
    create_console,
    resolve_cli_theme,
)


class TestResolveCliTheme:
    def test_explicit_tg_theme_light(self) -> None:
        assert resolve_cli_theme({"TG_THEME": "light"}) == "light"

    def test_explicit_tg_theme_dark(self) -> None:
        assert resolve_cli_theme({"TG_THEME": "dark"}) == "dark"

    def test_explicit_together_cli_theme(self) -> None:
        assert resolve_cli_theme({"TOGETHER_CLI_THEME": "light"}) == "light"

    def test_tg_theme_wins_over_colorfgbg(self) -> None:
        assert resolve_cli_theme({"TG_THEME": "dark", "COLORFGBG": "0;15"}) == "dark"

    def test_colorfgbg_light_background(self) -> None:
        assert resolve_cli_theme({"COLORFGBG": "0;15"}) == "light"
        assert resolve_cli_theme({"COLORFGBG": "15;7"}) == "light"

    def test_colorfgbg_dark_background(self) -> None:
        assert resolve_cli_theme({"COLORFGBG": "15;0"}) == "dark"
        assert resolve_cli_theme({"COLORFGBG": "7;0"}) == "dark"

    def test_default_is_dark(self) -> None:
        assert resolve_cli_theme({}) == "dark"

    def test_invalid_colorfgbg_falls_back_to_dark(self) -> None:
        assert resolve_cli_theme({"COLORFGBG": "default;default"}) == "dark"


class TestBuildThemeContrast:
    def test_light_theme_overrides_dim_and_white(self) -> None:
        theme = build_theme("light")
        assert "dim" in theme.styles
        assert "white" in theme.styles
        assert theme.styles["dim"].color is not None
        assert theme.styles["white"].color is not None
        # Must be solid colors, not ANSI dim / bright-white
        assert not theme.styles["dim"].dim
        assert theme.styles["dim"].color.name == _LIGHT_STYLES["dim"]
        assert theme.styles["white"].color.name == _LIGHT_STYLES["white"]

    def test_dark_theme_keeps_ansi_dim_behavior(self) -> None:
        theme = build_theme("dark")
        # Dark theme should not replace Rich's built-in dim/white with near-black
        assert "dim" not in _DARK_STYLES
        assert "white" not in _DARK_STYLES
        assert theme.styles["primary"].color is not None
        assert theme.styles["primary"].color.name == _DARK_STYLES["primary"]

    def test_dark_secondary_is_not_dimmed(self) -> None:
        theme = build_theme("dark")
        assert not theme.styles["secondary"].dim

    def test_light_theme_emits_dark_foreground_for_help_styles(self) -> None:
        console = Console(
            theme=build_theme("light"),
            force_terminal=True,
            color_system="truecolor",
            record=True,
            width=80,
        )
        console.print("[primary]name[/primary]")
        console.print("[secondary]type[/secondary]")
        console.print("[muted]description[/muted]")
        console.print("[dim]example[/dim]")
        console.print("[white]value[/white]")
        ansi = console.export_text(styles=True)

        # Light theme truecolor codes for the high-contrast palette
        assert "38;2;76;29;149" in ansi  # primary #4c1d95
        assert "38;2;17;24;39" in ansi  # secondary #111827
        assert "38;2;31;41;55" in ansi  # muted/dim #1f2937
        assert "38;2;0;0;0" in ansi  # white override #000000
        # Must not use ANSI dim or standard white on light theme for these tags
        assert "\x1b[2m" not in ansi
        assert "\x1b[37m" not in ansi

    def test_light_theme_body_text_meets_aaa_contrast_on_white(self) -> None:
        """Body styles should clear WCAG AAA (7:1) against white."""

        def relative_luminance(hex_color: str) -> float:
            raw = hex_color.lstrip("#")
            channels = [int(raw[i : i + 2], 16) / 255 for i in (0, 2, 4)]

            def linearize(channel: float) -> float:
                return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

            r, g, b = (linearize(c) for c in channels)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def contrast_on_white(hex_color: str) -> float:
            fg = relative_luminance(hex_color)
            bg = 1.0
            lighter, darker = max(fg, bg), min(fg, bg)
            return (lighter + 0.05) / (darker + 0.05)

        for key in ("primary", "secondary", "muted", "dim", "white"):
            style = _LIGHT_STYLES[key]
            hex_color = style.split()[-1]  # allow "bold #rrggbb"
            ratio = contrast_on_white(hex_color)
            assert ratio >= 7.0, f"{key}={style} contrast {ratio:.2f} < 7"


def test_console_replaces_characters_unsupported_by_stream_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    raw_output = io.BytesIO()
    cp1252_output = io.TextIOWrapper(raw_output, encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", cp1252_output)

    console = create_console()
    console.print("√ │ café")
    cp1252_output.flush()

    assert raw_output.getvalue().decode("cp1252") == "? ? café\n"
