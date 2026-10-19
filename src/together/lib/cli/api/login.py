"""`tg login` — OIDC device authorization (RFC 8628). See `together.lib.cli.auth`."""

from __future__ import annotations

import webbrowser
from typing import Any, Optional, Annotated

from cyclopts import Parameter
from rich.markup import escape as escape_rich_markup

from together import TogetherError
from together._utils._json import openapi_dumps
from together.lib.cli.auth import DeviceCode, TogetherAuth, issuer_from_base_url, note_credentials_path
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console
from together.lib.cli.utils._json_mode import plain_text
from together.lib.cli.utils._project_scope import CHOOSE_PROJECT_MESSAGE, offer_project_after_login


def _use_access_token(client: Any, access_token: str) -> None:
    """Send later calls in this process with the token just issued, not a placeholder or older session."""
    client.api_key = access_token
    http = getattr(client, "_client", None)
    if http is not None:
        http.auth = None


async def login(
    *,
    config: CLIConfigParameter,
    no_browser: Annotated[
        Optional[bool],
        Parameter(name="--no-browser", negative=(), help="Print the verification URL without opening a browser"),
    ] = False,
) -> None:
    """Log in with a browser using the OIDC device authorization grant.

    The issuer is the API base URL (`--base-url` / `TOGETHER_BASE_URL`, default
    https://api.together.ai). A legacy trailing `/v1` is stripped if present.
    """

    def prompt(code: DeviceCode) -> None:
        console.print("To authenticate, visit:")
        console.print(f"  [link={code.browser_url}]{code.browser_url}[/link]")
        console.print("")
        if not no_browser:
            try:
                opened = bool(webbrowser.open(code.browser_url))
            except Exception:
                opened = False
            if not opened:
                console.print(f"Open this URL to log in:\n{code.browser_url}")
        console.print("[dim]Waiting for authorization...[/dim]")

    with TogetherAuth() as auth:
        credentials = auth.login(issuer_from_base_url(str(config.client.base_url)), on_prompt=prompt)
    _use_access_token(config.client, credentials.access_token)

    switched: str | None = None
    switch_error: str | None = None
    try:
        switched = await offer_project_after_login(
            config.client,
            interactive=not config.json and not config.non_interactive,
        )
    except TogetherError as exc:
        switch_error = str(exc)

    note_credentials_path()
    if config.json:
        body: dict[str, str] = {"status": "ok"}
        if switched:
            body["project_id"] = switched
        else:
            body["next"] = plain_text(CHOOSE_PROJECT_MESSAGE)
        if switch_error:
            body["error"] = switch_error
        console.print_json(openapi_dumps(body).decode("utf-8"))
        return

    console.print("[green]Logged in.[/green]")
    if switched:
        console.print(f"[green]Switched to project[/green] [bold]{escape_rich_markup(switched)}[/bold]")
        return
    if switch_error:
        console.print(f"[red]Error:[/red] {escape_rich_markup(switch_error)}")
    console.print(CHOOSE_PROJECT_MESSAGE)
