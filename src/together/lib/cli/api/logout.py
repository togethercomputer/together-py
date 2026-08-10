from __future__ import annotations

from together.lib.cli.utils._console import console
from together.lib.cli.auth.credentials import credentials_path, clear_credentials


async def logout() -> None:
    """Remove locally stored OIDC credentials from `tg login`."""
    path = credentials_path()
    if clear_credentials(path):
        console.print(f"[green]✓[/green] Logged out (removed {path})")
    else:
        console.print("[dim]Already logged out[/dim]")
