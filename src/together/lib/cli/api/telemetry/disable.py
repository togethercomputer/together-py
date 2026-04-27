from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import (
    load_telemetry_config,
    save_telemetry_config,
    telemetry_config_path,
)
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


def disable(
    *,
    config: CLIConfigParameter,
) -> None:
    """Explicitly Disable telemetry"""
    cfg = load_telemetry_config()
    cfg["telemetry_enabled"] = False
    save_telemetry_config(cfg)
    path = telemetry_config_path()
    if config.json:
        console.print_json(openapi_dumps({"telemetry_enabled": False, "saved_to": str(path)}).decode("utf-8"))
        return
    console.print(f"Telemetry: [blue]Disabled[/blue]\n[dim](saved to {path})[/dim]")
