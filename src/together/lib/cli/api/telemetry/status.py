from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli._track_cli import (
    _env_telemetry_disabled,
    _config_telemetry_disabled,
)
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


def status(
    *,
    config: CLIConfigParameter,
) -> None:
    """Check to see if telemetry is enabled or disabled."""
    by_config = _config_telemetry_disabled()
    by_env = _env_telemetry_disabled()

    if config.json:
        if by_config:
            payload = {"telemetry": "disabled", "reason": "config_file"}
        elif by_env:
            payload = {"telemetry": "disabled", "reason": "environment"}
        else:
            payload = {"telemetry": "enabled"}
        console.print_json(openapi_dumps(payload).decode("utf-8"))
        return

    if by_config:
        console.print("Telemetry: [blue]Disabled[/blue]")
        return
    if by_env:
        console.print("Telemetry: [blue]Disabled[/blue] [dim](via environment variable)[/dim]")
        return
    console.print("Telemetry: [blue]Enabled[/blue]")
