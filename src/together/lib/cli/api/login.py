from __future__ import annotations

import os
from typing import Optional, Annotated

from cyclopts import Parameter

from together import TogetherError
from together.lib.cli.auth.oidc import (
    DEFAULT_OAUTH_SCOPES,
    format_expiry,
    login_with_oidc,
    discovery_url_from_base_url,
)
from together.lib.cli.utils._console import console


async def login(
    *,
    client_id: Annotated[
        Optional[str],
        Parameter(
            name="--client-id",
            help="OIDC client id for the Together CLI OAuth app (or TOGETHER_OAUTH_CLIENT_ID)",
            env_var="TOGETHER_OAUTH_CLIENT_ID",
        ),
    ] = None,
    client_secret: Annotated[
        Optional[str],
        Parameter(
            name="--client-secret",
            help="OIDC client secret when the CLI app is confidential (or TOGETHER_OAUTH_CLIENT_SECRET)",
            env_var="TOGETHER_OAUTH_CLIENT_SECRET",
        ),
    ] = None,
    scope: Annotated[
        str,
        Parameter(help="OIDC scopes to request"),
    ] = DEFAULT_OAUTH_SCOPES,
    no_browser: Annotated[
        bool,
        Parameter(name="--no-browser", negative=(), help="Print the login URL instead of opening a browser"),
    ] = False,
) -> None:
    """Authenticate with Together via OIDC (browser + PKCE) and store short-lived credentials.

    Access tokens live ~5 minutes and are refreshed invisibly using the stored refresh token.
    """
    discovery = discovery_url_from_base_url(os.environ.get("TOGETHER_BASE_URL"))
    try:
        credentials = login_with_oidc(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            discovery_url=discovery,
            open_browser=not no_browser,
        )
    except TogetherError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc

    console.print("[green]✓[/green] Logged in to Together")
    console.print(f"[dim]Access token expires {format_expiry(credentials)} (auto-refreshed)[/dim]")
