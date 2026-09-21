from __future__ import annotations

import importlib.util

from rich.markup import escape as escape_rich_markup

from together.lib.cli.utils._console import error_console

CLI_EXTRAS_INSTALL_COMMAND = 'uv tool install "together[cli]" --upgrade'
_CLI_EXTRA_MODULES = ("questionary", "yaml")


def has_cli_extras() -> bool:
    """Return True when the optional ``[cli]`` extra is installed."""
    return all(importlib.util.find_spec(name) is not None for name in _CLI_EXTRA_MODULES)


def inform_cli_extras_tip(*, non_interactive: bool) -> None:
    """Print a copy/paste install tip when the CLI was installed without extras."""
    if non_interactive or has_cli_extras():
        return

    command_text = escape_rich_markup(CLI_EXTRAS_INSTALL_COMMAND)
    error_console.print("\n[dim]Tip:[/dim] Install the CLI extras for a better experience with interactive prompts.")
    error_console.print(f"  [bold]{command_text}[/bold]")
