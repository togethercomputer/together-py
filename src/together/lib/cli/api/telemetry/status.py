from together.lib.cli._track_cli import (
    _env_telemetry_disabled,
    _config_telemetry_disabled,
)
from together.lib.cli.utils._console import console


def status() -> None:
    """Check to see if telemetry is enabled or disabled."""
    if _config_telemetry_disabled():
        console.print("Telemetry: [blue]Disabled[/blue]")
        return
    if _env_telemetry_disabled():
        console.print("Telemetry: [blue]Disabled[/blue] [dim](via environment variable)[/dim]")
        return
    console.print("Telemetry: [blue]Enabled[/blue]")
