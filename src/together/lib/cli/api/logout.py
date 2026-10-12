"""`tg logout` — wipe local credentials, then revoke the sessions (RFC 7009). See `together.lib.cli.auth`."""

from __future__ import annotations

from together._utils._json import openapi_dumps
from together.lib.cli.auth import TogetherAuth, note_credentials_path
from together.lib.cli.utils.config import CLIConfigParameter
from together.lib.cli.utils._console import console


def logout(*, config: CLIConfigParameter) -> None:
    """Remove the stored credentials and revoke their sessions.

    Always succeeds: local credentials are wiped first, and server-side revocation is best effort.
    """
    with TogetherAuth() as auth:
        auth.logout()
    note_credentials_path()
    if config.json:
        console.print_json(openapi_dumps({"status": "ok"}).decode("utf-8"))
        return
    console.print("Logged out.")
