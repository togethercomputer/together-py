from __future__ import annotations

import os
import ssl
import json as json_lib
import time
import base64
import socket
import hashlib
import secrets
import webbrowser
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, cast
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx

from together import TogetherError
from together.lib.cli.utils._console import console
from together.lib.cli.auth.credentials import (
    StoredCredentials,
    credentials_lock,
    load_credentials,
    save_credentials,
)

# Discovery document advertised at https://api.together.ai/.well-known/openid-configuration
_DEFAULT_API_ORIGIN = "https://api.together.ai"
_DEFAULT_REDIRECT_HOST = "localhost"
_DEFAULT_REDIRECT_PATH = "/login-callback"
_DEFAULT_REDIRECT_PORTS = (3000, 10001, 11110)
_TRUSTED_HOST_SUFFIXES = (".together.ai", ".together.xyz")
_ACCESS_TOKEN_REFRESH_SKEW_SECONDS = 30
DEFAULT_OAUTH_SCOPES = "openid email profile"


def discovery_url_from_base_url(base_url: Optional[str] = None) -> str:
    """Derive the OIDC discovery URL from an API base URL (…/v1 → origin/.well-known/…)."""
    origin = api_origin_from_base_url(base_url)
    return f"{origin}/.well-known/openid-configuration"


def api_origin_from_base_url(base_url: Optional[str] = None) -> str:
    raw = base_url or os.environ.get("TOGETHER_BASE_URL") or _DEFAULT_API_ORIGIN
    parsed = urllib.parse.urlparse(raw)
    if not parsed.scheme or not parsed.hostname:
        # bare host or path-only → treat as https origin
        if "://" not in raw:
            return f"https://{raw.rstrip('/')}"
        raise TogetherError(f"Invalid TOGETHER_BASE_URL for OIDC discovery: {raw}")
    return f"{parsed.scheme}://{parsed.netloc}"


def default_oauth_client_id() -> Optional[str]:
    return os.environ.get("TOGETHER_OAUTH_CLIENT_ID") or None


def default_oauth_client_secret() -> Optional[str]:
    return os.environ.get("TOGETHER_OAUTH_CLIENT_SECRET") or None


def _certifi_ssl_context() -> ssl.SSLContext:
    return httpx.create_ssl_context(trust_env=False)


def _http_json(
    url: str,
    data: Optional[dict[str, Any]] = None,
    ctx: Optional[ssl.SSLContext] = None,
    purpose: str = "request",
) -> dict[str, Any]:
    if data is None:
        req = urllib.request.Request(url, method="GET")
    else:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return cast("dict[str, Any]", json_lib.loads(resp.read().decode()))
    except urllib.error.HTTPError as exc:
        with exc:
            error_body = exc.read().decode(errors="replace")[:500]
            raise TogetherError(f"{purpose} failed: {url} returned HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        reason = str(exc.reason)
        if "CERTIFICATE_VERIFY_FAILED" in reason or "certificate verify failed" in reason.lower():
            raise TogetherError(
                f"{purpose} failed TLS verification for {url}. "
                "The CLI uses its bundled CA store; upgrade the Together CLI if this persists."
            ) from exc
        raise TogetherError(f"{purpose} failed for {url}: {reason}") from exc


def _is_loopback(host: Optional[str]) -> bool:
    return (host or "").lower() in ("localhost", "127.0.0.1", "::1")


def _is_trusted_together_url(url: str, *, allow_loopback: bool = False) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if not host or parsed.username is not None or parsed.password is not None:
        return False
    if parsed.query or parsed.fragment:
        return False
    if allow_loopback and _is_loopback(host) and parsed.scheme in ("http", "https"):
        return True
    if parsed.scheme != "https":
        return False
    if host in ("together.ai", "together.xyz"):
        return True
    return any(host.endswith(suffix) for suffix in _TRUSTED_HOST_SUFFIXES)


def _validate_discovery_endpoint(endpoint: Any, name: str, *, allow_loopback: bool = False) -> str:
    if not isinstance(endpoint, str) or not endpoint:
        raise TogetherError(f"OIDC discovery returned no valid {name}")
    if not _is_trusted_together_url(endpoint, allow_loopback=allow_loopback):
        raise TogetherError(f"OIDC discovery {name} must be an https Together URL")
    return endpoint


def fetch_openid_configuration(discovery_url: Optional[str] = None) -> dict[str, Any]:
    url = discovery_url or discovery_url_from_base_url()
    allow_loopback = _is_loopback(urllib.parse.urlparse(url).hostname)
    if not _is_trusted_together_url(url, allow_loopback=allow_loopback):
        raise TogetherError(f"OIDC discovery URL is not a trusted Together URL: {url}")
    disc = _http_json(url, ctx=_certifi_ssl_context(), purpose="OIDC discovery")
    _validate_discovery_endpoint(
        disc.get("authorization_endpoint"), "authorization endpoint", allow_loopback=allow_loopback
    )
    _validate_discovery_endpoint(disc.get("token_endpoint"), "token endpoint", allow_loopback=allow_loopback)
    return disc


def _redirect_uri_for_port(port: int) -> str:
    return f"http://{_DEFAULT_REDIRECT_HOST}:{port}{_DEFAULT_REDIRECT_PATH}"


def _localhost_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection((_DEFAULT_REDIRECT_HOST, port), timeout=0.2):
            return True
    except OSError:
        return False


def _callback_server(handler: type[BaseHTTPRequestHandler]) -> tuple[HTTPServer, str]:
    for port in _DEFAULT_REDIRECT_PORTS:
        if _localhost_port_in_use(port):
            continue
        try:
            return HTTPServer((_DEFAULT_REDIRECT_HOST, port), handler), _redirect_uri_for_port(port)
        except OSError:
            continue

    ports = "/".join(str(port) for port in _DEFAULT_REDIRECT_PORTS)
    raise TogetherError(
        f"OIDC login needs a local callback port, but {ports} are all in use. "
        "Stop the process using one of these ports and rerun `tg login`."
    )


def _callback_code(request_path: str, expected_state: str) -> Optional[str]:
    parsed_request = urllib.parse.urlparse(request_path)
    if parsed_request.path != _DEFAULT_REDIRECT_PATH:
        return None
    query = urllib.parse.parse_qs(parsed_request.query)
    if "error" in query:
        desc = query.get("error_description", query.get("error", ["unknown"]))[0]
        raise TogetherError(f"OIDC authorization failed: {desc}")
    callback_state = query.get("state", [""])[0]
    if "code" not in query or not secrets.compare_digest(callback_state.encode(), expected_state.encode()):
        return None
    return query["code"][0]


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    # RFC 7636: code_verifier is 43-128 unreserved chars; token_urlsafe(64) is fine.
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


def _credentials_from_token_response(
    tok: dict[str, Any],
    *,
    client_id: str,
    token_endpoint: str,
    issuer: Optional[str],
    previous: Optional[StoredCredentials] = None,
) -> StoredCredentials:
    access_token = tok.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise TogetherError(f"token endpoint returned no access_token: {tok}")

    refresh_token = tok.get("refresh_token")
    if not isinstance(refresh_token, str) or not refresh_token:
        if previous and previous.refresh_token:
            refresh_token = previous.refresh_token
        else:
            raise TogetherError(
                "token endpoint returned no refresh_token. "
                "The CLI needs a refresh token to renew short-lived access tokens invisibly."
            )

    expires_in = tok.get("expires_in", 300)
    try:
        expires_in_s = int(expires_in)
    except (TypeError, ValueError) as exc:
        raise TogetherError(f"token endpoint returned invalid expires_in: {expires_in}") from exc

    return StoredCredentials(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=time.time() + max(expires_in_s, 1),
        token_type=str(tok.get("token_type") or "Bearer"),
        id_token=tok.get("id_token") if isinstance(tok.get("id_token"), str) else (previous.id_token if previous else None),
        scope=tok.get("scope") if isinstance(tok.get("scope"), str) else (previous.scope if previous else None),
        client_id=client_id,
        token_endpoint=token_endpoint,
        issuer=issuer if isinstance(issuer, str) else (previous.issuer if previous else None),
    )


def login_with_oidc(
    *,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    scope: str = DEFAULT_OAUTH_SCOPES,
    discovery_url: Optional[str] = None,
    open_browser: bool = True,
) -> StoredCredentials:
    """Run authorization-code + PKCE against Together OIDC and persist credentials."""
    resolved_client_id = client_id or default_oauth_client_id()
    if not resolved_client_id:
        raise TogetherError(
            "OIDC client_id is not configured. Set TOGETHER_OAUTH_CLIENT_ID or pass --client-id. "
            "This is the Together CLI OAuth application id (app_…) registered in UMS."
        )
    resolved_secret = client_secret if client_secret is not None else default_oauth_client_secret()

    ctx = _certifi_ssl_context()
    disc = fetch_openid_configuration(discovery_url)
    authorization_endpoint = _validate_discovery_endpoint(
        disc.get("authorization_endpoint"), "authorization endpoint"
    )
    token_endpoint = _validate_discovery_endpoint(disc.get("token_endpoint"), "token endpoint")
    issuer = disc.get("issuer") if isinstance(disc.get("issuer"), str) else None

    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    captured: dict[str, str] = {}

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            try:
                code = _callback_code(self.path, state)
            except TogetherError as exc:
                captured["error"] = str(exc)
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Login failed. You can close this tab.")
                return
            if code is not None:
                captured["code"] = code
                captured["state"] = state
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Login complete. You can close this tab and return to the terminal.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid login callback.")

        @override
        def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
            pass

    server, redirect_uri = _callback_server(_Handler)
    params = {
        "response_type": "code",
        "client_id": resolved_client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = authorization_endpoint + "?" + urllib.parse.urlencode(params)
    console.print("[dim]Opening browser for Together login…[/dim]")
    console.print(f"[dim]{auth_url}[/dim]")
    if open_browser and not webbrowser.open(auth_url):
        console.print(f"Open this URL to log in:\n{auth_url}")
    elif not open_browser:
        console.print(f"Open this URL to log in:\n{auth_url}")

    try:
        server.handle_request()
    finally:
        server.server_close()

    if captured.get("error"):
        raise TogetherError(captured["error"])
    if not captured.get("code") or captured.get("state") != state:
        raise TogetherError(
            "Browser login did not complete. Keep this terminal running until the browser "
            "redirects back to localhost, then try `tg login` again."
        )

    token_data: dict[str, Any] = {
        "grant_type": "authorization_code",
        "code": captured["code"],
        "redirect_uri": redirect_uri,
        "client_id": resolved_client_id,
        "code_verifier": verifier,
    }
    if resolved_secret:
        token_data["client_secret"] = resolved_secret

    tok = _http_json(token_endpoint, data=token_data, ctx=ctx, purpose="OIDC token exchange")
    credentials = _credentials_from_token_response(
        tok,
        client_id=resolved_client_id,
        token_endpoint=token_endpoint,
        issuer=issuer,
    )
    with credentials_lock():
        save_credentials(credentials)
    return credentials


def _access_token_needs_refresh(credentials: StoredCredentials, *, skew_seconds: int = _ACCESS_TOKEN_REFRESH_SKEW_SECONDS) -> bool:
    return time.time() >= (credentials.expires_at - skew_seconds)


def refresh_access_token(
    credentials: StoredCredentials,
    *,
    client_secret: Optional[str] = None,
) -> StoredCredentials:
    """Exchange a refresh token for a new short-lived access token."""
    if not credentials.token_endpoint:
        # Fall back to discovery when older credential files omit the endpoint.
        disc = fetch_openid_configuration()
        token_endpoint = _validate_discovery_endpoint(disc.get("token_endpoint"), "token endpoint")
    else:
        token_endpoint = credentials.token_endpoint

    client_id = credentials.client_id or default_oauth_client_id()
    if not client_id:
        raise TogetherError(
            "Stored credentials are missing client_id and TOGETHER_OAUTH_CLIENT_ID is unset. "
            "Run `tg login` again."
        )

    resolved_secret = client_secret if client_secret is not None else default_oauth_client_secret()
    token_data: dict[str, Any] = {
        "grant_type": "refresh_token",
        "refresh_token": credentials.refresh_token,
        "client_id": client_id,
    }
    if resolved_secret:
        token_data["client_secret"] = resolved_secret

    tok = _http_json(
        token_endpoint,
        data=token_data,
        ctx=_certifi_ssl_context(),
        purpose="OIDC token refresh",
    )
    refreshed = _credentials_from_token_response(
        tok,
        client_id=client_id,
        token_endpoint=token_endpoint,
        issuer=credentials.issuer,
        previous=credentials,
    )
    save_credentials(refreshed)
    return refreshed


def resolve_access_token(*, client_secret: Optional[str] = None) -> Optional[str]:
    """Return a valid access token from disk, refreshing invisibly when near expiry."""
    with credentials_lock():
        credentials = load_credentials()
        if credentials is None:
            return None
        if not _access_token_needs_refresh(credentials):
            return credentials.access_token
        try:
            refreshed = refresh_access_token(credentials, client_secret=client_secret)
        except TogetherError:
            # Stale/invalid refresh token — treat as logged out for auth resolution.
            return None
        return refreshed.access_token


def format_expiry(credentials: StoredCredentials) -> str:
    dt = datetime.fromtimestamp(credentials.expires_at, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
