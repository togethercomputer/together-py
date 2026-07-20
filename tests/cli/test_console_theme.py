from __future__ import annotations

from rich.console import Console

from together.lib.cli.utils._console import (
    _DARK_STYLES,
    _LIGHT_STYLES,
    build_theme,
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
        assert (
            resolve_cli_theme({"TG_THEME": "dark", "COLORFGBG": "0;15"}) == "dark"
        )

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

        # Light theme truecolor codes for the chosen palette
        assert "38;2;109;40;217" in ansi  # primary #6d28d9
        assert "38;2;91;33;182" in ansi  # secondary #5b21b6
        assert "38;2;75;85;99" in ansi  # muted/dim #4b5563
        assert "38;2;17;24;39" in ansi  # white override #111827
        # Must not use ANSI dim or standard white on light theme for these tags
        assert "\x1b[2m" not in ansi
        assert "\x1b[37m" not in ansi
