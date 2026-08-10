"""CLI OIDC authentication helpers for `tg login` / credential refresh."""

from together.lib.cli.auth.oidc import (
    DEFAULT_OAUTH_SCOPES,
    login_with_oidc,
    resolve_access_token,
)
from together.lib.cli.auth.credentials import (
    StoredCredentials,
    credentials_path,
    load_credentials,
    save_credentials,
    clear_credentials,
)

__all__ = [
    "DEFAULT_OAUTH_SCOPES",
    "StoredCredentials",
    "clear_credentials",
    "credentials_path",
    "load_credentials",
    "login_with_oidc",
    "resolve_access_token",
    "save_credentials",
]
