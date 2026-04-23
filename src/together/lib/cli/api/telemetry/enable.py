from __future__ import annotations

from together.lib.cli._track_cli import (
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
)
from together.lib.cli.utils._console import console


def enable() -> None:
    """Enable telemetry"""
    cfg = load_telemetry_config()
    cfg["telemetry_enabled"] = True
    save_telemetry_config(cfg)
    console.print(f"Telemetry: [blue]Enabled[/blue]\n[dim](saved to {telemetry_config_path()})[/dim]")
