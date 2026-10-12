"""`tg login` authentication for the CLI: the credential store, the OAuth flows, and HTTP auth.

Commands call one method on `TogetherAuth`:

    tg login   -> TogetherAuth.login(issuer, on_prompt=...)
    tg switch  -> TogetherAuth.switch(project_id)
    tg logout  -> TogetherAuth.logout()
    (launcher) -> TogetherAuth.refresh(), plus `StoredTokenAuth` for one retry on 401

Layout of this module:

- Credential store (`StoredCredentials`, `CredentialStore`): a kubeconfig-shaped file with a
  list of named entries and a `current` pointer. The login entry (no `project_id`) holds the
  refresh token; a project entry from `tg switch` holds only its project-scoped token.

      {
        "version": 1,
        "current": "proj_abc",
        "credentials": [
          {"name": "default", "access_token": "...", "refresh_token": "...", ...},
          {"name": "proj_abc", "access_token": "...", "project_id": "proj_abc", ...}
        ]
      }

  Older files are migrated on read: a flat credential object becomes the `default` entry, and
  entries that merged `project_access_token` into a copy of the login tokens are split.
- `_OIDCClient`: discovery and form POSTs against one issuer's endpoints.
- `TogetherAuth`: the operations. Tokens are only ever sent to the issuer that minted them.
- `StoredTokenAuth`: httpx auth that refreshes once and retries when the stored token gets a 401.

This module is CLI-only; the SDK clients never read the credential store.
"""

from __future__ import annotations

import os
import sys
import json
import time
import asyncio
import urllib.parse
from typing import Any, List, Callable, Optional, Generator, AsyncGenerator, cast
from pathlib import Path
from dataclasses import asdict, replace, dataclass
from typing_extensions import override

import httpx

from together import TogetherError
from together._version import __version__
from together.lib.utils import log_debug

DEFAULT_ISSUER = "https://api.together.ai"
# OAuth client id of the Together CLI app registration. Every `tg login` uses it.
CLI_CLIENT_ID = "app_CfXyxzEgNqQmH1PJEr2Xw"
# Undocumented override of `CLI_CLIENT_ID`, e.g. for an app registered in another environment.
_CLIENT_ID_ENV = "OIDC_ID"
DEFAULT_CREDENTIALS_NAME = "default"

_PRODUCTION_API_BASE_URL = "https://api.together.ai/v1"
_CONFIG_DIR_NAME = "together"
_CREDENTIALS_FILE_NAME = "credentials.json"
_FILE_VERSION = 1
_USER_AGENT = f"together-cli/{__version__}"

_DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"
_REFRESH_GRANT = "refresh_token"
_TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
# Together vendor grant renewing a `tg switch` project (ForkV1 child) session token via
# `ums.sessions.verifyV1`. Sends the project token as `access_token`; returns no refresh token.
_SESSION_GRANT = "urn:together.ai:params:oauth:grant-type:session"
_ACCESS_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:access_token"
_JWT_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:jwt"

_DEFAULT_POLL_INTERVAL = 5
_MAX_POLL_INTERVAL = 30
_DEFAULT_DEVICE_EXPIRES_IN = 600
# Refresh this many seconds before the recorded expiry to absorb clock skew and request latency.
_EXPIRY_SKEW_SECONDS = 60


# --------------------------------------------------------------------------------------------
# Credential store
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class StoredCredentials:
    access_token: str
    token_type: str = "Bearer"
    refresh_token: Optional[str] = None
    id_token: Optional[str] = None
    expires_at: Optional[int] = None
    issuer: Optional[str] = None
    client_id: Optional[str] = None
    project_id: Optional[str] = None
    name: Optional[str] = None

    @property
    def entry_name(self) -> str:
        """Key of this entry in the store: explicit name, else project id, else `default`."""
        return self.name or self.project_id or DEFAULT_CREDENTIALS_NAME

    @property
    def api_base_url(self) -> Optional[str]:
        """API base URL of the environment whose issuer minted these credentials (`{issuer}/v1`)."""
        if not self.issuer:
            return None
        return self.issuer.rstrip("/") + "/v1"

    def require_issuer(self) -> str:
        """The issuer that minted these credentials. Stored tokens are only ever sent back to it."""
        if not self.issuer:
            raise TogetherError(
                f"Stored credentials '{self.entry_name}' do not record their issuer. Run `tg login` again."
            )
        return self.issuer


@dataclass(frozen=True)
class CredentialStore:
    credentials: List[StoredCredentials]
    current: Optional[str] = None

    @classmethod
    def load(cls) -> CredentialStore:
        path = credentials_path()
        if not path.is_file():
            return cls(credentials=[])
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls(credentials=[])
        if not isinstance(data, dict):
            return cls(credentials=[])
        payload = cast(dict[str, Any], data)

        raw_entries = payload.get("credentials")
        if not isinstance(raw_entries, list):
            # Legacy single-credential file.
            legacy = _parse_entries({**payload, "name": _str_or_none(payload.get("name")) or DEFAULT_CREDENTIALS_NAME})
            if not legacy:
                return cls(credentials=[])
            return cls(credentials=legacy, current=legacy[-1].entry_name)

        entries: List[StoredCredentials] = []
        seen: set[str] = set()
        for raw in cast(List[Any], raw_entries):
            for entry in _parse_entries(raw):
                # First wins: an explicit login entry beats one split out of a legacy merged entry.
                if entry.entry_name in seen:
                    continue
                seen.add(entry.entry_name)
                entries.append(entry)
        current = _str_or_none(payload.get("current"))
        if current not in seen:
            current = None
        return cls(credentials=entries, current=current)

    def save(self) -> Path:
        """Write the store atomically with 0600 permissions; an empty store deletes the file."""
        path = credentials_path()
        if not self.credentials:
            if path.is_file():
                path.unlink()
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        entries: List[dict[str, Any]] = []
        for entry in self.credentials:
            named = replace(entry, name=entry.entry_name)
            entries.append({key: value for key, value in asdict(named).items() if value is not None})
        payload: dict[str, Any] = {"version": _FILE_VERSION, "credentials": entries}
        if self.current is not None:
            payload["current"] = self.current
        tmp = path.with_name(path.name + ".tmp")
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(tmp, flags, 0o600)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
        except Exception:
            try:
                tmp.unlink()
            except OSError:
                pass
            raise
        tmp.replace(path)
        if sys.platform != "win32":
            try:
                path.chmod(0o600)
            except OSError:
                pass
        return path

    def get(self, name: str) -> Optional[StoredCredentials]:
        for entry in self.credentials:
            if entry.entry_name == name:
                return entry
        return None

    def current_credentials(self) -> Optional[StoredCredentials]:
        if self.current is None:
            return None
        return self.get(self.current)

    def login_credentials(self) -> Optional[StoredCredentials]:
        """The `tg login` entry: the one without a project, preferring the `default` name."""
        logins = [entry for entry in self.credentials if entry.project_id is None]
        for entry in logins:
            if entry.entry_name == DEFAULT_CREDENTIALS_NAME:
                return entry
        return logins[0] if logins else None

    def upsert(self, credentials: StoredCredentials) -> CredentialStore:
        """Insert or replace the entry named `credentials.entry_name` and make it current."""
        name = credentials.entry_name
        entries = [entry for entry in self.credentials if entry.entry_name != name]
        entries.append(replace(credentials, name=name))
        return CredentialStore(credentials=entries, current=name)

    def replace(self, credentials: StoredCredentials) -> CredentialStore:
        """Replace the entry named `credentials.entry_name`, keeping `current` where it was."""
        entries = [credentials if entry.entry_name == credentials.entry_name else entry for entry in self.credentials]
        return CredentialStore(credentials=entries, current=self.current)


def note_credentials_path() -> None:
    """Record the credentials file path. Only `--debug` prints it."""
    from together.lib.cli.utils._debug import is_enabled, log_debug_note

    if is_enabled():
        log_debug_note(f"credentials file {credentials_path()}")


def credentials_path() -> Path:
    override = os.environ.get("TOGETHER_CREDENTIALS_PATH")
    if override:
        return Path(override)
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Together" / _CREDENTIALS_FILE_NAME
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / _CONFIG_DIR_NAME / _CREDENTIALS_FILE_NAME
    return Path.home() / ".config" / _CONFIG_DIR_NAME / _CREDENTIALS_FILE_NAME


def load_stored_credentials() -> Optional[StoredCredentials]:
    """The entry selected by `current`, if any."""
    return CredentialStore.load().current_credentials()


def save_stored_credentials(credentials: StoredCredentials) -> Path:
    """Insert or replace `credentials` in the store and make it current."""
    return CredentialStore.load().upsert(credentials).save()


def load_stored_base_url() -> Optional[str]:
    """API base URL implied by the current entry's issuer, or None when it is production.

    Returning None for production keeps the SDK default (and its non-overridden v2 routing).
    """
    stored = load_stored_credentials()
    base_url = stored.api_base_url if stored is not None else None
    if base_url is None or base_url == _PRODUCTION_API_BASE_URL:
        return None
    return base_url


def issuer_from_base_url(base_url: str) -> str:
    """OIDC issuer for an API base URL: the base URL without its trailing `/v1`.

    Inverse of `StoredCredentials.api_base_url`, which maps a stored issuer back to `{issuer}/v1`.
    """
    parsed = urllib.parse.urlparse(base_url)
    if not parsed.scheme or not parsed.netloc:
        raise TogetherError(f"Base URL must be an absolute http(s) URL, got {base_url!r}")
    path = parsed.path.rstrip("/")
    if path.endswith("/v1"):
        path = path[: -len("/v1")]
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _str_or_none(value: Any) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def _int_or_none(value: Any) -> Optional[int]:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _parse_entries(data: Any) -> List[StoredCredentials]:
    """Parse one stored entry; a legacy merged project entry yields [login, project]."""
    if not isinstance(data, dict):
        return []
    payload = cast(dict[str, Any], data)
    access_token = _str_or_none(payload.get("access_token"))
    if access_token is None:
        return []
    issuer = _str_or_none(payload.get("issuer"))
    client_id = _str_or_none(payload.get("client_id"))
    project_id = _str_or_none(payload.get("project_id"))
    name = _str_or_none(payload.get("name"))
    entry = StoredCredentials(
        access_token=access_token,
        token_type=_str_or_none(payload.get("token_type")) or "Bearer",
        refresh_token=_str_or_none(payload.get("refresh_token")),
        id_token=_str_or_none(payload.get("id_token")),
        expires_at=_int_or_none(payload.get("expires_at")),
        issuer=issuer,
        client_id=client_id,
        project_id=project_id,
        name=name,
    )
    project_token = _str_or_none(payload.get("project_access_token"))
    if project_token is None:
        return [entry]
    # Legacy merged entry: the top-level tokens are the login's, the project token rides along.
    login = replace(entry, project_id=None, name=DEFAULT_CREDENTIALS_NAME)
    project = StoredCredentials(
        access_token=project_token,
        token_type=_str_or_none(payload.get("project_token_type")) or "Bearer",
        expires_at=_int_or_none(payload.get("project_expires_at")),
        issuer=issuer,
        client_id=client_id,
        project_id=project_id,
        name=None if name == DEFAULT_CREDENTIALS_NAME else name,
    )
    return [login, project]


# --------------------------------------------------------------------------------------------
# OIDC protocol for one issuer
# --------------------------------------------------------------------------------------------


def _is_together_host(hostname: Optional[str]) -> bool:
    if hostname is None:
        return False
    host = hostname.lower()
    return host == "together.ai" or host.endswith(".together.ai")


def _is_loopback_host(hostname: Optional[str]) -> bool:
    return hostname in {"localhost", "127.0.0.1", "::1"}


def _validate_endpoint(endpoint: Any, issuer: str, name: str) -> str:
    if not isinstance(endpoint, str) or not endpoint:
        raise TogetherError(f"OIDC discovery returned no valid {name}")
    parsed = urllib.parse.urlparse(endpoint)
    issuer_parsed = urllib.parse.urlparse(issuer)
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise TogetherError(f"OIDC discovery {name} must not include credentials, query, or fragment")
    if _is_loopback_host(parsed.hostname) and parsed.scheme in {"http", "https"}:
        return endpoint
    if parsed.scheme != "https" or parsed.hostname is None:
        raise TogetherError(f"OIDC discovery {name} must be an HTTPS URL")
    if _is_together_host(issuer_parsed.hostname):
        if not _is_together_host(parsed.hostname):
            raise TogetherError(f"OIDC discovery {name} must use a together.ai host")
        return endpoint
    if parsed.hostname != issuer_parsed.hostname or parsed.port != issuer_parsed.port:
        raise TogetherError(f"OIDC discovery {name} must use the trusted issuer origin")
    return endpoint


class _OIDCClient:
    """Discovery plus form POSTs to one issuer's token, device, and revocation endpoints."""

    def __init__(self, http: httpx.Client, issuer: str) -> None:
        self.http = http
        self.issuer = issuer
        self._discovery: Optional[dict[str, Any]] = None

    def discover(self, *, require_device: bool = False) -> dict[str, Any]:
        if self._discovery is None:
            url = self.issuer.rstrip("/") + "/.well-known/openid-configuration"
            _, document = self.request("GET", url, purpose="OIDC discovery")
            document["token_endpoint"] = _validate_endpoint(
                document.get("token_endpoint"), self.issuer, "token endpoint"
            )
            if "device_authorization_endpoint" in document:
                document["device_authorization_endpoint"] = _validate_endpoint(
                    document.get("device_authorization_endpoint"), self.issuer, "device authorization endpoint"
                )
            if "revocation_endpoint" in document:
                document["revocation_endpoint"] = _validate_endpoint(
                    document.get("revocation_endpoint"), self.issuer, "revocation endpoint"
                )
            self._discovery = document
        if require_device and "device_authorization_endpoint" not in self._discovery:
            raise TogetherError(
                "This Together environment does not advertise a device_authorization_endpoint. "
                "Device login is not available here yet."
            )
        return self._discovery

    @property
    def token_endpoint(self) -> str:
        return str(self.discover()["token_endpoint"])

    @property
    def device_authorization_endpoint(self) -> str:
        return str(self.discover(require_device=True)["device_authorization_endpoint"])

    @property
    def revocation_endpoint(self) -> str:
        advertised = self.discover().get("revocation_endpoint")
        if isinstance(advertised, str) and advertised:
            return advertised
        token_endpoint = urllib.parse.urlparse(self.token_endpoint)
        fallback = f"{token_endpoint.scheme}://{token_endpoint.netloc}/oauth/revoke"
        return _validate_endpoint(fallback, self.issuer, "revocation endpoint")

    def token(self, data: dict[str, str], *, purpose: str) -> tuple[int, dict[str, Any]]:
        """POST a grant to the token endpoint; OAuth error bodies are returned, not raised."""
        return self.request("POST", self.token_endpoint, data=data, purpose=purpose, accept_error_body=True)

    def request(
        self,
        method: str,
        url: str,
        *,
        data: Optional[dict[str, str]] = None,
        purpose: str,
        accept_error_body: bool = False,
        allow_empty_body: bool = False,
    ) -> tuple[int, dict[str, Any]]:
        headers = {"Accept": "application/json", "User-Agent": _USER_AGENT}
        content: Optional[str] = None
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            content = urllib.parse.urlencode(data)
        # `--debug` logs this call (headers and bodies, secrets redacted) via the client's event hooks.
        try:
            response = self.http.request(method, url, headers=headers, content=content)
        except httpx.RequestError as exc:
            raise TogetherError(f"{purpose} failed for {url}: {exc}") from exc

        body: Any
        try:
            body = response.json()
        except ValueError:
            body = None

        if response.is_success:
            if allow_empty_body and not isinstance(body, dict):
                return response.status_code, {}
            if not isinstance(body, dict):
                raise TogetherError(f"{purpose} returned a non-JSON response from {url}")
            return response.status_code, cast(dict[str, Any], body)

        if accept_error_body and isinstance(body, dict):
            return response.status_code, cast(dict[str, Any], body)

        snippet = response.text[:300] if response.text else ""
        raise TogetherError(f"{purpose} failed: {url} returned HTTP {response.status_code}: {snippet}")


def _oauth_error(body: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    error = body.get("error")
    description = body.get("error_description")
    return (
        error if isinstance(error, str) and error else None,
        description if isinstance(description, str) and description else None,
    )


def _expires_at(expires_in: Any, now: int) -> Optional[int]:
    if isinstance(expires_in, bool) or not isinstance(expires_in, int) or expires_in <= 0:
        return None
    return now + int(expires_in)


# --------------------------------------------------------------------------------------------
# Operations
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class DeviceCode:
    """What the user needs to approve a device login in the browser."""

    user_code: str
    verification_uri: str
    browser_url: str


class TogetherAuth:
    """`tg login` session operations against the on-disk credential store.

    Pass `http_client` (e.g. with a mock transport) and `clock` to control I/O and time; otherwise
    an httpx client is created on first use and closed by `close()` / the context manager.
    """

    def __init__(self, *, http_client: Optional[httpx.Client] = None, clock: Callable[[], float] = time.time) -> None:
        self._http = http_client
        self._owns_http = http_client is None
        self._clock = clock
        self._oidc_clients: dict[str, _OIDCClient] = {}

    def __enter__(self) -> TogetherAuth:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_http and self._http is not None:
            self._http.close()
            self._http = None

    def _oidc(self, issuer: str) -> _OIDCClient:
        if issuer not in self._oidc_clients:
            if self._http is None:
                from together.lib.cli.utils._debug import install_sync_http_debug_hooks

                self._http = httpx.Client(timeout=30.0, follow_redirects=True)
                # `--debug`: summary on stderr, full headers and bodies (secrets redacted) in the log file.
                install_sync_http_debug_hooks(self._http)
            self._oidc_clients[issuer] = _OIDCClient(self._http, issuer)
        return self._oidc_clients[issuer]

    def _now(self) -> int:
        return int(self._clock())

    def _expired(self, expires_at: Optional[int]) -> bool:
        return expires_at is not None and expires_at - _EXPIRY_SKEW_SECONDS <= self._now()

    # -- tg login ------------------------------------------------------------------------------

    def login(
        self,
        issuer: str,
        *,
        on_prompt: Callable[[DeviceCode], None],
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> StoredCredentials:
        """RFC 8628 device login. Replaces every stored entry with the new login and returns it.

        An existing session is logged out first. Otherwise its tokens are dropped from disk
        while remaining valid, and a later `tg logout` can no longer revoke them.
        """
        if CredentialStore.load().credentials:
            self.logout()
        client_id = cli_client_id()
        oidc = self._oidc(issuer)
        _, issued = oidc.request(
            "POST",
            oidc.device_authorization_endpoint,
            data={"client_id": client_id},
            purpose="device authorization",
        )
        device_code = _str_or_none(issued.get("device_code"))
        user_code = _str_or_none(issued.get("user_code"))
        verification_uri = _str_or_none(issued.get("verification_uri"))
        if device_code is None:
            raise TogetherError("device authorization endpoint returned no device_code")
        if user_code is None:
            raise TogetherError("device authorization endpoint returned no user_code")
        if verification_uri is None:
            raise TogetherError("device authorization endpoint returned no verification_uri")
        on_prompt(
            DeviceCode(
                user_code=user_code,
                verification_uri=verification_uri,
                browser_url=_str_or_none(issued.get("verification_uri_complete")) or verification_uri,
            )
        )

        expires_in = issued.get("expires_in")
        interval = issued.get("interval")
        if not isinstance(expires_in, int) or expires_in <= 0:
            expires_in = _DEFAULT_DEVICE_EXPIRES_IN
        if not isinstance(interval, int) or interval <= 0:
            interval = _DEFAULT_POLL_INTERVAL
        deadline = monotonic() + float(expires_in)
        while True:
            if monotonic() >= deadline:
                raise TogetherError("Device login timed out. Restart `tg login` and try again.")
            status, body = oidc.token(
                {"grant_type": _DEVICE_GRANT, "device_code": device_code, "client_id": client_id},
                purpose="device token poll",
            )
            if status == 200:
                credentials = self._login_credentials(body, issuer, client_id)
                # A fresh login replaces every stored entry, including project entries from `tg switch`.
                CredentialStore(credentials=[credentials], current=credentials.entry_name).save()
                return credentials

            error, _ = _oauth_error(body)
            if error == "slow_down":
                next_interval = body.get("interval")
                if isinstance(next_interval, int) and next_interval > 0:
                    interval = min(next_interval, _MAX_POLL_INTERVAL)
                else:
                    interval = min(interval + 5, _MAX_POLL_INTERVAL)
            elif error == "authorization_pending":
                pass
            elif error == "access_denied":
                raise TogetherError("Device login was denied in the browser.")
            elif error == "expired_token":
                raise TogetherError("Device login expired. Restart `tg login` and try again.")
            elif error == "invalid_grant":
                raise TogetherError("Device login could not be completed. Restart `tg login` and try again.")
            else:
                raise TogetherError(f"Device login failed: {error or f'HTTP {status}'}")

            remaining = deadline - monotonic()
            if remaining <= 0:
                raise TogetherError("Device login timed out. Restart `tg login` and try again.")
            sleep(min(float(interval), remaining))

    def _login_credentials(self, body: dict[str, Any], issuer: str, client_id: str) -> StoredCredentials:
        access_token = _str_or_none(body.get("access_token"))
        if access_token is None:
            if isinstance(body.get("response"), str):
                # An encrypted (JWE) token response; the CLI does not send a key to decrypt one with.
                raise TogetherError("token endpoint returned an encrypted response, which this CLI version cannot read")
            raise TogetherError("token endpoint returned no access_token")
        return StoredCredentials(
            access_token=access_token,
            token_type=_str_or_none(body.get("token_type")) or "Bearer",
            refresh_token=_str_or_none(body.get("refresh_token")),
            id_token=_str_or_none(body.get("id_token")),
            expires_at=_expires_at(body.get("expires_in"), self._now()),
            issuer=issuer,
            client_id=client_id,
        )

    # -- tg switch -----------------------------------------------------------------------------

    def switch(self, project_id: str) -> StoredCredentials:
        """RFC 8693 exchange of the login token for a project-scoped token; stores it as current.

        The project entry holds only the project token; nothing is copied from the login entry.
        """
        target = project_id.strip()
        if not target:
            raise TogetherError("A project ID is required")
        login = CredentialStore.load().login_credentials()
        if login is None:
            raise TogetherError("Not logged in. Run `tg login` first.")
        # The exchange needs a live login token; refresh it first if it has expired.
        login = self.refresh(name=login.entry_name) or login
        project = self._exchange(login, target)
        CredentialStore.load().upsert(project).save()
        return project

    def _exchange(self, login: StoredCredentials, project_id: str) -> StoredCredentials:
        if login.project_id is not None:
            raise TogetherError("Project switch needs the `tg login` credentials, not a project entry")
        issuer = login.require_issuer()
        client_id = _client_id(login)
        status, body = self._oidc(issuer).token(
            {
                "grant_type": _TOKEN_EXCHANGE_GRANT,
                "subject_token": login.access_token,
                "subject_token_type": _JWT_TOKEN_TYPE if login.access_token.startswith("eyJ") else _ACCESS_TOKEN_TYPE,
                "resource": project_id,
                "client_id": client_id,
            },
            purpose="project token exchange",
        )
        if status != 200:
            raise _exchange_error(status, body)
        access_token = _str_or_none(body.get("access_token"))
        if access_token is None:
            raise TogetherError("token endpoint returned no project access_token")
        return StoredCredentials(
            access_token=access_token,
            token_type=_str_or_none(body.get("token_type")) or "Bearer",
            expires_at=_expires_at(body.get("expires_in"), self._now()),
            issuer=issuer,
            client_id=client_id,
            project_id=project_id,
            name=project_id,
        )

    # -- refresh (launcher, 401 retry, tg switch) ----------------------------------------------

    def refresh(self, *, force: bool = False, name: Optional[str] = None) -> Optional[StoredCredentials]:
        """Renew the current entry (or the one called `name`) when expired, or always with `force`.

        A login entry uses the refresh_token grant; a project entry uses the session grant with its
        own project token. Returns the updated entry, or None when nothing needed (or could be)
        refreshed. Raises TogetherError if a refresh was attempted and failed.
        """
        store = CredentialStore.load()
        target = store.get(name) if name is not None else store.current_credentials()
        if target is None or not (force or self._expired(target.expires_at)):
            return None
        if target.project_id is None and not target.refresh_token:
            return None
        updated = self._renew_project(target) if target.project_id is not None else self._refresh_login(target)
        # Persist immediately: UMS rotates the login refresh token, and replaying the old one
        # is treated as theft and revokes the session (IAM-2612).
        CredentialStore.load().replace(updated).save()
        return updated

    def _refresh_login(self, login: StoredCredentials) -> StoredCredentials:
        assert login.refresh_token
        status, body = self._oidc(login.require_issuer()).token(
            {
                "grant_type": _REFRESH_GRANT,
                # Together extension to RFC 6749 §6: UMS binds the access/refresh pair to one
                # session and rejects a refresh without the access token in use.
                "access_token": login.access_token,
                "refresh_token": login.refresh_token,
                "client_id": _client_id(login),
            },
            purpose="token refresh",
        )
        if status != 200:
            error, detail = _oauth_error(body)
            code = error or f"HTTP {status}"
            if error in {"invalid_grant", "invalid_client"} or status == 401:
                raise TogetherError(
                    f"Login expired ({code}: {detail or 'refresh rejected'}). Run `tg login` and try again."
                )
            raise TogetherError(f"Token refresh failed ({code}){f': {detail}' if detail else ''}")
        access_token = _str_or_none(body.get("access_token"))
        if access_token is None:
            raise TogetherError("token endpoint returned no access_token on refresh")
        return replace(
            login,
            access_token=access_token,
            token_type=_str_or_none(body.get("token_type")) or login.token_type,
            # Servers that rotate refresh tokens return a new one; otherwise the old one stays valid.
            refresh_token=_str_or_none(body.get("refresh_token")) or login.refresh_token,
            id_token=_str_or_none(body.get("id_token")) or login.id_token,
            expires_at=_expires_at(body.get("expires_in"), self._now()),
        )

    def _renew_project(self, project: StoredCredentials) -> StoredCredentials:
        assert project.project_id
        status, body = self._oidc(project.require_issuer()).token(
            {"grant_type": _SESSION_GRANT, "access_token": project.access_token, "client_id": _client_id(project)},
            purpose="project session refresh",
        )
        if status != 200:
            error, detail = _oauth_error(body)
            code = error or f"HTTP {status}"
            if error in {"invalid_grant", "invalid_client"} or status == 401:
                raise TogetherError(
                    f"Project session expired ({code}: {detail or 'renewal rejected'}). "
                    f"Run `tg switch {project.project_id}` to get a new project token."
                )
            raise TogetherError(f"Project token refresh failed ({code}){f': {detail}' if detail else ''}")
        access_token = _str_or_none(body.get("access_token"))
        if access_token is None:
            raise TogetherError("token endpoint returned no access_token on project session refresh")
        return replace(
            project,
            access_token=access_token,
            token_type=_str_or_none(body.get("token_type")) or project.token_type,
            expires_at=_expires_at(body.get("expires_in"), self._now()),
        )

    # -- tg logout -----------------------------------------------------------------------------

    def logout(self) -> None:
        """Wipe every local credential immediately, then revoke the sessions server-side.

        Revocation is best effort and never raises: the local credentials are already gone, which
        is what logging out guarantees. Each `tg login` session is revoked through its login entry
        (its `tg switch` project tokens are children of it); a project entry whose issuer has no
        login entry is revoked on its own.
        """
        store = CredentialStore.load()
        CredentialStore(credentials=[]).save()
        login_issuers = {entry.issuer for entry in store.credentials if entry.project_id is None}
        for entry in store.credentials:
            if entry.project_id is not None and entry.issuer in login_issuers:
                continue
            try:
                # Tokens go back only to the issuer that minted them.
                self.revoke(entry, issuer=entry.require_issuer())
            except Exception as exc:
                log_debug("Server-side revoke during logout failed", entry=entry.entry_name, error=exc)

    def revoke(self, credentials: StoredCredentials, *, issuer: str) -> None:
        """RFC 7009 revocation at `issuer`: the refresh token when there is one, else the access token."""
        oidc = self._oidc(issuer)
        if credentials.refresh_token:
            token, hint = credentials.refresh_token, "refresh_token"
        else:
            token, hint = credentials.access_token, "access_token"
        status, body = oidc.request(
            "POST",
            oidc.revocation_endpoint,
            data={"token": token, "token_type_hint": hint, "client_id": _client_id(credentials)},
            purpose="token revocation",
            accept_error_body=True,
            allow_empty_body=True,
        )
        if status != 200:
            error, detail = _oauth_error(body)
            raise TogetherError(detail or f"Logout revoke failed: {error or f'HTTP {status}'}")


def cli_client_id() -> str:
    """The CLI's OAuth client id: `$OIDC_ID` when set, else `CLI_CLIENT_ID`."""
    return os.environ.get(_CLIENT_ID_ENV) or CLI_CLIENT_ID


def _client_id(credentials: StoredCredentials) -> str:
    """The client id stored with the credentials (tokens are bound to it), else the CLI's."""
    return credentials.client_id or cli_client_id()


def _exchange_error(status: int, body: dict[str, Any]) -> TogetherError:
    error, detail = _oauth_error(body)
    if error == "unsupported_grant_type":
        return TogetherError(detail or "Project switching is not available in this Together environment yet.")
    if error in {"invalid_grant", "access_denied"}:
        return TogetherError(detail or "Could not switch to that project. Check the project ID and your access.")
    if status == 401 or error == "invalid_client":
        return TogetherError(detail or "Login expired. Run `tg login` and try again.")
    if error:
        return TogetherError(detail or f"Project switch failed: {error}")
    return TogetherError(f"Project switch failed: HTTP {status}")


def _force_refresh_current() -> Optional[StoredCredentials]:
    with TogetherAuth() as auth:
        return auth.refresh(force=True)


# --------------------------------------------------------------------------------------------
# HTTP auth: one refresh + retry on 401
# --------------------------------------------------------------------------------------------


def _bearer(header: Optional[str]) -> Optional[str]:
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    return token if scheme.lower() == "bearer" and token else None


def _replayable(request: httpx.Request) -> bool:
    try:
        request.content  # noqa: B018
    except httpx.RequestNotRead:
        return False
    return True


class StoredTokenAuth(httpx.Auth):
    """On a 401 for a request sent with the stored `tg login` token, refresh once and retry.

    Requests authenticated with anything else (e.g. presigned upload URLs) pass through untouched.
    """

    def __init__(
        self,
        token: str,
        on_token: Callable[[str], None],
        refresh: Callable[[], Optional[StoredCredentials]] = _force_refresh_current,
    ) -> None:
        self._token = token
        self._stale: set[str] = set()
        self._on_token = on_token
        self._refresh = refresh
        self._lock = asyncio.Lock()
        # Set when the 401 retry's refresh is rejected. A 401 after that is a dead
        # session, not "this token needs a project".
        self.refresh_failure: Optional[TogetherError] = None

    def _sent_stored_token(self, request: httpx.Request) -> Optional[str]:
        sent = _bearer(request.headers.get("authorization"))
        if sent is not None and (sent == self._token or sent in self._stale):
            return sent
        return None

    def _do_refresh(self, sent: str) -> bool:
        if sent != self._token:
            # Another request already refreshed; just retry with the new token.
            return True
        try:
            updated = self._refresh()
        except TogetherError as exc:
            log_debug("Stored token refresh after 401 failed", error=exc)
            self.refresh_failure = exc
            return False
        if updated is None:
            return False
        self.refresh_failure = None
        self._stale.add(self._token)
        self._token = updated.access_token
        self._on_token(self._token)
        return True

    def _retry(self, request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request

    @override
    def sync_auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        response = yield request
        if response.status_code != 401 or not _replayable(request):
            return
        sent = self._sent_stored_token(request)
        if sent is None or not self._do_refresh(sent):
            return
        yield self._retry(request)

    @override
    async def async_auth_flow(self, request: httpx.Request) -> AsyncGenerator[httpx.Request, httpx.Response]:
        response = yield request
        if response.status_code != 401 or not _replayable(request):
            return
        sent = self._sent_stored_token(request)
        if sent is None:
            return
        async with self._lock:
            refreshed = await asyncio.to_thread(self._do_refresh, sent)
        if not refreshed:
            return
        yield self._retry(request)
