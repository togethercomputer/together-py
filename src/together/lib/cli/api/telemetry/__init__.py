from __future__ import annotations

import click
from rich import print

from together.lib.cli._track_cli import (
    auto_track_command,
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
    _env_telemetry_disabled,
    _config_telemetry_disabled,
)


@click.group("telemetry", short_help="CLI telemetry commands")
def telemetry() -> None:
    """Together collects usage data by default and can be controlled with this command, or by setting TOGETHER_TELEMETRY_DISABLED=1"""


@telemetry.command("status")
@auto_track_command
def telemetry_status() -> None:
    """Check to see if telemetry is enabled or disabled."""
    if _config_telemetry_disabled():
        print("Telemetry: [blue]Disabled[/blue]")
        return
    if _env_telemetry_disabled():
        print("Telemetry: [blue]Disabled[/blue] [dim](via environment variable)[/dim]")
        return
    print("Telemetry: [blue]Enabled[/blue]")


@telemetry.command("disable")
@auto_track_command
def telemetry_disable() -> None:
    """Explicitly Disable telemetry"""
    cfg = load_telemetry_config()
    cfg["telemetry_enabled"] = False
    save_telemetry_config(cfg)
    print(f"[blue]Telemetry disabled[/blue] [dim](saved to {telemetry_config_path()})[/dim]")


@telemetry.command("enable")
@auto_track_command
def telemetry_enable() -> None:
    """Enable telemetry"""
    cfg = load_telemetry_config()
    cfg["telemetry_enabled"] = True
    save_telemetry_config(cfg)
    print(f"[blue]Telemetry enabled[/blue] [dim](saved to {telemetry_config_path()})[/dim]")
