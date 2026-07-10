"""`tg beta clusters ssh` — SSH into a Together cluster using a short-lived,
OIDC-signed SSH certificate. No API key, no long-lived SSH key, no
control-plane contact: every coordinate is derived from the cluster's Dex URL.

Flow:
    1. OIDC login against the cluster's Dex issuer (browser, PKCE) -> id_token
    2. generate an ephemeral SSH keypair
    3. POST the public key + id_token to the cluster's step-ca `/ssh/sign`
       -> short-lived SSH user certificate (principal = email)
    4. exec `ssh` through the bastion to the target host

The host trusts step-ca's CA and maps the cert's email principal to the POSIX
login, so no `authorized_keys` or per-user key distribution is involved.
"""

from __future__ import annotations

import os
import re
import ssl
import json as json_lib
import stat
import shlex
import base64
import socket
import hashlib
import secrets
import tempfile
import contextlib
import subprocess
import webbrowser
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Annotated, cast
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx
from cyclopts import Parameter
from filelock import FileLock

from together import TogetherError
from together.lib.cli.utils._console import console

_CERT_ALGO = {
    "ecdsa": "ecdsa-sha2-nistp256-cert-v01@openssh.com",
    "ed25519": "ssh-ed25519-cert-v01@openssh.com",
}
_DEFAULT_REDIRECT_HOST = "localhost"
_DEFAULT_REDIRECT_PATH = "/login-callback"
_DEFAULT_REDIRECT_PORTS = (3000, 10001, 11110)
_DEFAULT_CACHE_ROOT = os.path.join(os.path.expanduser("~"), ".together", "ssh")
_CERT_REFRESH_SKEW = timedelta(minutes=5)
_CACHE_LOCK_TIMEOUT_SECONDS = 600
_TRUSTED_DEX_SUFFIX = ".together.ai"


def _http_json(
    url: str,
    data: Optional[dict[str, Any]] = None,
    ctx: Optional[ssl.SSLContext] = None,
    purpose: str = "request",
) -> dict[str, Any]:
    """GET (data=None) or form-POST JSON helper using stdlib only."""
    if data is None:
        req = urllib.request.Request(url, method="GET")
    else:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return cast("dict[str, Any]", json_lib.loads(resp.read().decode()))
    except urllib.error.HTTPError as exc:
        with exc:
            error_body = exc.read().decode(errors="replace")[:300]
            if exc.code == 404:
                raise TogetherError(
                    f"{purpose} failed: {url} returned 404. "
                    "Check that the cluster OIDC/Dex endpoint is ready and that the copied OIDC issuer URL is current. "
                    "If this came from the UI, try refreshing the cluster page and make sure your Together CLI is up to date "
                    "(`uv tool install together --upgrade` or `pip install --upgrade together`)."
                ) from exc
            raise TogetherError(f"{purpose} failed: {url} returned HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        reason = str(exc.reason)
        if "CERTIFICATE_VERIFY_FAILED" in reason or "certificate verify failed" in reason.lower():
            raise TogetherError(
                f"{purpose} failed TLS verification for {url}. "
                "The CLI uses its bundled CA store, so the endpoint may be serving an incomplete or untrusted "
                "certificate chain. Upgrade the Together CLI, then contact support if the error continues."
            ) from exc
        raise TogetherError(f"{purpose} failed for {url}: {reason}") from exc


def _certifi_ssl_context() -> ssl.SSLContext:
    return httpx.create_ssl_context(trust_env=False)


def _parse_dex_url(dex_url: str) -> tuple[urllib.parse.ParseResult, str]:
    parsed = urllib.parse.urlparse(dex_url)
    path_parts = parsed.path.strip("/").split("/")
    try:
        port = parsed.port
    except ValueError as exc:
        raise TogetherError("DEX_URL contains an invalid port") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or not parsed.hostname.startswith("dex.")
        or not parsed.hostname.endswith(_TRUSTED_DEX_SUFFIX)
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or len(path_parts) != 1
        or re.fullmatch(r"[A-Za-z0-9-]+", path_parts[0]) is None
        or parsed.query
        or parsed.fragment
    ):
        raise TogetherError("DEX_URL must be an HTTPS Together Dex issuer URL with one cluster id path")
    return parsed, path_parts[0]


def _derive(dex_url: str) -> tuple[str, str]:
    """Derive (ca_url, bastion) from the cluster's Dex issuer URL.

    A Dex issuer looks like `https://dex.<base>/<cluster-id>`, from which:
        ca_url  = https://dex.<base>/step-<cluster-id>
        bastion = ssh.<cluster-id>.<base>
    """
    parsed, cluster_id = _parse_dex_url(dex_url)
    hostname = cast("str", parsed.hostname)
    base = hostname.removeprefix("dex.")
    return f"https://{hostname}/step-{cluster_id}", f"ssh.{cluster_id}.{base}"


def _cluster_id(dex_url: str) -> str:
    _, cluster_id = _parse_dex_url(dex_url)
    return cluster_id


def _redirect_uri_for_port(port: int) -> str:
    return f"http://{_DEFAULT_REDIRECT_HOST}:{port}{_DEFAULT_REDIRECT_PATH}"


def _localhost_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection((_DEFAULT_REDIRECT_HOST, port), timeout=0.2):
            return True
    except OSError:
        return False


def _callback_server(
    handler: type[BaseHTTPRequestHandler],
) -> tuple[HTTPServer, str]:
    for port in _DEFAULT_REDIRECT_PORTS:
        # HTTPServer can bind IPv4 while another process owns the same port on
        # IPv6. The browser may resolve localhost to that other listener.
        if _localhost_port_in_use(port):
            continue
        candidate_uri = _redirect_uri_for_port(port)
        try:
            return HTTPServer((_DEFAULT_REDIRECT_HOST, port), handler), candidate_uri
        except OSError:
            continue

    ports = "/".join(str(port) for port in _DEFAULT_REDIRECT_PORTS)
    raise TogetherError(
        f"OIDC login needs a local callback port, but {ports} are all in use. "
        "Stop the process using one of these ports and rerun the command."
    )


def _validate_discovery_endpoint(endpoint: Any, issuer: str, name: str) -> str:
    if not isinstance(endpoint, str):
        raise TogetherError(f"OIDC discovery returned no valid {name}")
    endpoint_url = urllib.parse.urlparse(endpoint)
    issuer_url = urllib.parse.urlparse(issuer)
    if (
        endpoint_url.scheme != "https"
        or endpoint_url.hostname != issuer_url.hostname
        or endpoint_url.port != issuer_url.port
        or endpoint_url.username is not None
        or endpoint_url.password is not None
        or endpoint_url.query
        or endpoint_url.fragment
    ):
        raise TogetherError(f"OIDC discovery {name} must use the trusted issuer origin")
    return endpoint


def _callback_code(request_path: str, expected_state: str) -> Optional[str]:
    parsed_request = urllib.parse.urlparse(request_path)
    if parsed_request.path != _DEFAULT_REDIRECT_PATH:
        return None
    query = urllib.parse.parse_qs(parsed_request.query)
    callback_state = query.get("state", [""])[0]
    if "code" not in query or not secrets.compare_digest(callback_state.encode(), expected_state.encode()):
        return None
    return query["code"][0]


def _pkce_login(issuer: str, client_id: str, scope: str) -> str:
    """Authorization-code + PKCE flow against Dex. Returns the raw id_token."""
    ctx = _certifi_ssl_context()
    disc = _http_json(issuer.rstrip("/") + "/.well-known/openid-configuration", ctx=ctx, purpose="OIDC discovery")
    authorization_endpoint = _validate_discovery_endpoint(
        disc.get("authorization_endpoint"),
        issuer,
        "authorization endpoint",
    )
    token_endpoint = _validate_discovery_endpoint(disc.get("token_endpoint"), issuer, "token endpoint")
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    captured: dict[str, str] = {}

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            code = _callback_code(self.path, state)
            if code is not None:
                captured["code"] = code
                captured["state"] = state
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Login complete. You can close this tab.")
            else:
                self.send_response(400)
                self.end_headers()

        @override
        def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
            # Silence the default per-request logging to stderr.
            pass

    # Bind before starting authorization, then reuse this exact URI for the token
    # exchange. PKCE prevents another local process from redeeming an intercepted code.
    server, redirect_uri = _callback_server(_Handler)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = authorization_endpoint + "?" + urllib.parse.urlencode(params)
    console.print(f"[dim]Opening browser for login: {issuer}[/dim]")
    if not webbrowser.open(auth_url):
        console.print(f"Open this URL to log in:\n{auth_url}")
    server.handle_request()
    server.server_close()

    if not captured.get("code") or captured.get("state") != state:
        raise TogetherError(
            "Browser login did not complete. No valid cached SSH certificate is available. "
            "Please log into Together Web and rerun this command. If the browser shows "
            "'localhost refused to connect', the CLI callback listener likely exited; rerun "
            "the command and keep the terminal process running until login completes."
        )
    tok = _http_json(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": captured["code"],
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": verifier,
        },
        ctx=ctx,
        purpose="OIDC token exchange",
    )
    if "id_token" not in tok:
        raise TogetherError(f"token endpoint returned no id_token: {tok}")
    return str(tok["id_token"])


def _sign(ca_url: str, ott: str, pub_blob: str, ctx: Optional[ssl.SSLContext]) -> str:
    """POST to step-ca /ssh/sign. Returns the base64 cert blob."""
    body = json_lib.dumps({"publicKey": pub_blob, "OTT": ott, "certType": "user"}).encode()
    req = urllib.request.Request(ca_url.rstrip("/") + "/ssh/sign", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            out = json_lib.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        with e:
            raise TogetherError(f"step-ca /ssh/sign failed ({e.code}): {e.read().decode()[:300]}") from e
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "CERTIFICATE_VERIFY_FAILED" in reason or "certificate verify failed" in reason.lower():
            raise TogetherError(
                f"step-ca /ssh/sign failed TLS verification for {ca_url}. "
                "The CLI uses its bundled CA store. Check the endpoint certificate chain, or pass the expected "
                "private CA certificate with --ca-root."
            ) from e
        raise TogetherError(f"step-ca /ssh/sign failed for {ca_url}: {reason}") from e
    if "crt" not in out:
        raise TogetherError(f"step-ca returned no crt: {out}")
    return str(out["crt"])


def _read_pubkey_blob(key_path: str) -> str:
    public_key_path = key_path + ".pub"
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(public_key_path, flags)
    except OSError as exc:
        raise TogetherError(f"could not securely open cached public key: {public_key_path}") from exc
    with os.fdopen(fd) as f:
        file_stat = os.fstat(f.fileno())
        if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_uid != os.geteuid():
            raise TogetherError("cached public key must be a regular file owned by the current user")
        if stat.S_IMODE(file_stat.st_mode) & 0o022:
            raise TogetherError("cached public key must not be group- or world-writable")
        parts = f.read().split()
    if len(parts) < 2:
        raise TogetherError("cached public key is malformed")
    return parts[1]


def _validate_private_key(key_path: str) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(key_path, flags)
    except OSError as exc:
        raise TogetherError(f"could not securely open cached private key: {key_path}") from exc
    with os.fdopen(fd) as f:
        file_stat = os.fstat(f.fileno())
        if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_uid != os.geteuid():
            raise TogetherError("cached private key must be a regular file owned by the current user")
        if stat.S_IMODE(file_stat.st_mode) & 0o077:
            raise TogetherError("cached private key permissions must be 600")


def _gen_keypair(key_path: str, key_type: str) -> str:
    """ssh-keygen a keypair. Returns pubkey_blob."""
    subprocess.run(
        ["ssh-keygen", "-t", key_type, "-f", key_path, "-N", "", "-q", "-C", "together-ssh"],
        check=True,
    )
    os.chmod(key_path, 0o600)
    return _read_pubkey_blob(key_path)


def _get_or_create_keypair(key_path: str, key_type: str) -> str:
    public_key_path = key_path + ".pub"
    try:
        _validate_private_key(key_path)
        return _read_pubkey_blob(key_path)
    except TogetherError:
        pass
    for path in (key_path, public_key_path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    return _gen_keypair(key_path, key_type)


def _prepare_cache_directory(path: str) -> None:
    os.makedirs(path, mode=0o700, exist_ok=True)
    directory_stat = os.lstat(path)
    if not stat.S_ISDIR(directory_stat.st_mode) or directory_stat.st_uid != os.geteuid():
        raise TogetherError("SSH cache directory must be owned by the current user and must not be a symlink")
    os.chmod(path, 0o700)


def _cache_paths(dex_url: str, login: str, key_type: str, cache_root: str) -> tuple[str, str]:
    cluster = _cluster_id(dex_url)
    issuer_hash = hashlib.sha256(dex_url.encode()).hexdigest()[:12]
    safe_login = urllib.parse.quote(login, safe="")
    cache_dir = os.path.join(cache_root, f"{cluster}-{issuer_hash}", safe_login, key_type)
    return os.path.join(cache_dir, "id"), os.path.join(cache_dir, "id-cert.pub")


def _cert_validity_window(cert_path: str) -> Optional[tuple[datetime, datetime]]:
    if not os.path.exists(cert_path):
        return None
    result = subprocess.run(
        ["ssh-keygen", "-L", "-f", cert_path],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    if "Valid: forever" in result.stdout:
        return datetime.min, datetime.max
    match = re.search(r"Valid:\s+from\s+([0-9T:\-+]+)\s+to\s+([0-9T:\-+]+)", result.stdout)
    if match is None:
        return None
    try:
        return datetime.fromisoformat(match.group(1)), datetime.fromisoformat(match.group(2))
    except ValueError:
        return None


def _cert_is_valid(cert_path: str) -> bool:
    validity_window = _cert_validity_window(cert_path)
    if validity_window is None:
        return False
    valid_after, valid_until = validity_window
    now = datetime.now(valid_after.tzinfo)
    return valid_after <= now and valid_until > now + _CERT_REFRESH_SKEW


def _validate_ssh_destination(login: str, host: str, bastion: str) -> None:
    if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", login) is None:
        raise TogetherError("SSH login contains unsupported characters")
    hostname_pattern = r"[A-Za-z0-9][A-Za-z0-9._-]*"
    if re.fullmatch(hostname_pattern, host) is None:
        raise TogetherError("SSH target host contains unsupported characters")
    if re.fullmatch(hostname_pattern, bastion) is None:
        raise TogetherError("SSH bastion host contains unsupported characters")


def _ssh_command(
    login: str,
    host: str,
    bastion: str,
    key_path: str,
    cert_path: str,
    known_hosts_path: str,
    remote_command: tuple[str, ...],
) -> list[str]:
    _validate_ssh_destination(login, host, bastion)
    common = ["-i", key_path, "-o", f"CertificateFile={cert_path}", "-o", "IdentitiesOnly=yes"]
    proxy_common = common + ["-o", "StrictHostKeyChecking=ask"]
    proxy = (
        "ssh "
        + " ".join(shlex.quote(arg) for arg in proxy_common)
        + f" -W %h:%p {shlex.quote(login)}@{shlex.quote(bastion)}"
    )
    inner_verification = [
        "-o",
        "StrictHostKeyChecking=ask",
        "-o",
        f"UserKnownHostsFile={known_hosts_path}",
        "-o",
        f"HostKeyAlias={host}.{bastion}",
    ]
    return (
        ["ssh"]
        + common
        + inner_verification
        + ["-o", f"ProxyCommand={proxy}", "--", f"{login}@{host}"]
        + list(remote_command)
    )


def _shell_command(args: list[str]) -> str:
    return " ".join(shlex.quote(arg) for arg in args)


def _validate_ssh_alias(alias: str) -> None:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", alias) is None:
        raise TogetherError("SSH config alias must contain only letters, numbers, dots, underscores, and hyphens")


def _ssh_config_value(value: str) -> str:
    if "\n" in value or "\r" in value:
        raise TogetherError("SSH config values must not contain newlines")
    if not any(char.isspace() for char in value) and '"' not in value and "\\" not in value:
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _ssh_config_entry(
    alias: str,
    login: str,
    host: str,
    bastion: str,
    key_path: str,
    cert_path: str,
    known_hosts_path: str,
) -> str:
    _validate_ssh_alias(alias)
    _validate_ssh_destination(login, host, bastion)
    common = ["-i", key_path, "-o", f"CertificateFile={cert_path}", "-o", "IdentitiesOnly=yes"]
    proxy_common = common + ["-o", "StrictHostKeyChecking=ask"]
    proxy = (
        "ssh "
        + " ".join(shlex.quote(arg) for arg in proxy_common)
        + f" -W %h:%p {shlex.quote(login)}@{shlex.quote(bastion)}"
    )
    return "\n".join(
        [
            f"Host {alias}",
            f"  HostName {_ssh_config_value(host)}",
            f"  User {_ssh_config_value(login)}",
            f"  IdentityFile {_ssh_config_value(key_path)}",
            f"  CertificateFile {_ssh_config_value(cert_path)}",
            "  IdentitiesOnly yes",
            "  StrictHostKeyChecking ask",
            f"  UserKnownHostsFile {_ssh_config_value(known_hosts_path)}",
            f"  HostKeyAlias {_ssh_config_value(f'{host}.{bastion}')}",
            f"  ProxyCommand {proxy}",
        ]
    )


def _replace_managed_host_entry(config: str, alias: str, entry: str) -> str:
    _validate_ssh_alias(alias)
    lines = config.splitlines()
    out: list[str] = []
    i = 0
    replaced = False

    while i < len(lines):
        line = lines[i]
        if line.strip() == f"Host {alias}":
            out.extend(entry.splitlines())
            replaced = True
            i += 1
            while i < len(lines) and not lines[i].startswith("Host "):
                i += 1
            continue
        out.append(line)
        i += 1

    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.extend(entry.splitlines())

    return "\n".join(out).rstrip() + "\n"


def _atomic_write(path: str, content: str, mode: int) -> None:
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", dir=os.path.dirname(path), text=True)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
    finally:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass


def _read_owned_text_file(path: str, purpose: str) -> str:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise TogetherError(f"could not securely open {purpose}: {path}") from exc
    with os.fdopen(fd) as f:
        file_stat = os.fstat(f.fileno())
        if not stat.S_ISREG(file_stat.st_mode) or file_stat.st_uid != os.geteuid():
            raise TogetherError(f"{purpose} must be a regular file owned by the current user")
        if stat.S_IMODE(file_stat.st_mode) & 0o022:
            raise TogetherError(f"{purpose} must not be group- or world-writable")
        return f.read()


def _ensure_include(main_config_path: str, include_path: str) -> None:
    os.makedirs(os.path.dirname(main_config_path), mode=0o700, exist_ok=True)
    include_line = f"Include {_ssh_config_value(include_path)}"
    write_path = main_config_path

    if os.path.islink(main_config_path):
        write_path = os.path.realpath(main_config_path)
        if not os.path.exists(write_path):
            raise TogetherError("main SSH config symlink target must exist")

    if os.path.exists(write_path):
        content = _read_owned_text_file(write_path, "main SSH config")
        if any(line.strip() == include_line for line in content.splitlines()):
            return
        new_content = include_line + "\n" + content
    else:
        new_content = include_line + "\n"

    _atomic_write(write_path, new_content, 0o600)


def _write_ssh_config(alias: str, entry: str, cache_root: str) -> tuple[str, str]:
    managed_config = os.path.join(cache_root, "config")
    main_config = os.path.join(os.path.expanduser("~"), ".ssh", "config")
    lock_path = os.path.join(os.path.dirname(main_config), ".together-config.lock")
    os.makedirs(os.path.dirname(managed_config), mode=0o700, exist_ok=True)
    os.makedirs(os.path.dirname(lock_path), mode=0o700, exist_ok=True)

    with FileLock(lock_path, timeout=_CACHE_LOCK_TIMEOUT_SECONDS):
        if os.path.lexists(managed_config):
            content = _read_owned_text_file(managed_config, "managed SSH config")
        else:
            content = ""

        _atomic_write(managed_config, _replace_managed_host_entry(content, alias, entry), 0o600)
        _ensure_include(main_config, managed_config)

    return managed_config, main_config


async def ssh(
    dex_url: Annotated[str, Parameter(help="Cluster Dex issuer URL: https://dex.<base>/<cluster-id>")],
    *remote_command: Annotated[
        str,
        Parameter(allow_leading_hyphen=True, help="Remote command and arguments; never parsed as SSH client options"),
    ],
    login: Annotated[str, Parameter(name=["--login", "-l"], help="POSIX login / SSH username on the cluster")],
    host: Annotated[
        str,
        Parameter(
            help="Target host on the cluster (any hostname reachable through the bastion; e.g. slurm-login or a worker)"
        ),
    ] = "slurm-login",
    client_id: Annotated[str, Parameter(help="Dex public client id")] = "together-cli",
    scope: Annotated[str, Parameter(help="OIDC scopes")] = "openid email",
    key_type: Annotated[str, Parameter(help="Ephemeral key type (ecdsa is KMS-compatible)")] = "ecdsa",
    ca_root: Annotated[Optional[str], Parameter(help="step-ca root cert (PEM) for TLS")] = None,
    cache: Annotated[bool, Parameter(help="Cache SSH key/certificate and reuse while valid")] = True,
    refresh: Annotated[bool, Parameter(negative=False, help="Force refreshing the cached SSH certificate")] = False,
    cache_dir: Annotated[Optional[str], Parameter(help="Directory for cached SSH keys/certificates")] = None,
    print_ssh_command: Annotated[
        bool, Parameter(negative=False, help="Print the underlying ssh command instead of executing it")
    ] = False,
    ssh_config_alias: Annotated[
        Optional[str], Parameter(help="Print an ssh_config Host entry for this alias instead of executing ssh")
    ] = None,
    write_ssh_config: Annotated[
        bool,
        Parameter(
            negative=False, help="Write/update the alias in ~/.together/ssh/config and include it from ~/.ssh/config"
        ),
    ] = False,
) -> None:
    """SSH into a Together cluster, identified only by its Dex URL.

    DEX_URL is the cluster's Dex issuer (https://dex.<base>/<cluster-id>); the
    step-ca endpoint and bastion are derived from it. Logs into Dex, has step-ca
    sign an ephemeral key, then SSHes through the bastion as --login. Never
    contacts the control plane. Anything after DEX_URL is passed through to ssh.
    """
    issuer = dex_url
    ca_url, bastion = _derive(dex_url)
    if not cache and (print_ssh_command or ssh_config_alias is not None or write_ssh_config):
        raise TogetherError(
            "--print-ssh-command, --ssh-config-alias, and --write-ssh-config require cached key/cert files"
        )
    if write_ssh_config and ssh_config_alias is None:
        raise TogetherError("--write-ssh-config requires --ssh-config-alias")
    if key_type not in _CERT_ALGO:
        raise TogetherError(f"unsupported SSH key type: {key_type}")

    if ca_root:
        ca_ctx = ssl.create_default_context(cafile=ca_root)
    else:
        ca_ctx = _certifi_ssl_context()

    cache_root = os.path.expanduser(cache_dir or _DEFAULT_CACHE_ROOT)
    if cache:
        key_path, cert_path = _cache_paths(issuer, login, key_type, cache_root)
        _prepare_cache_directory(os.path.dirname(key_path))
    else:
        tmp = tempfile.TemporaryDirectory(prefix="together-ssh-")
        key_path = os.path.join(tmp.name, "id")
        cert_path = key_path + "-cert.pub"

    cache_lock = (
        FileLock(key_path + ".lock", timeout=_CACHE_LOCK_TIMEOUT_SECONDS) if cache else contextlib.nullcontext()
    )
    with cache_lock:
        if cache and not refresh and os.path.exists(key_path) and _cert_is_valid(cert_path):
            console.print(f"[dim]Using cached SSH certificate: {cert_path}[/dim]")
        else:
            pub_blob = _get_or_create_keypair(key_path, key_type)
            if cache:
                console.print(
                    "[yellow]No valid cached SSH certificate found. Opening browser for Together login.[/yellow]"
                )
                console.print(
                    "[dim]Keep this terminal command running until login completes. "
                    "If you are logged out of Together Web, log in in the browser first.[/dim]"
                )
            ott = _pkce_login(issuer, client_id, scope)
            crt = _sign(ca_url, ott, pub_blob, ca_ctx)
            _atomic_write(cert_path, f"{_CERT_ALGO[key_type]} {crt} together-ssh\n", 0o644)

    known_hosts_path = os.path.join(os.path.dirname(key_path), "known_hosts")
    cmd = _ssh_command(login, host, bastion, key_path, cert_path, known_hosts_path, remote_command)
    if ssh_config_alias is not None:
        entry = _ssh_config_entry(
            ssh_config_alias,
            login,
            host,
            bastion,
            key_path,
            cert_path,
            known_hosts_path,
        )
        if write_ssh_config:
            managed_config, main_config = _write_ssh_config(ssh_config_alias, entry, cache_root)
            console.print(f"[green]Wrote SSH alias '{ssh_config_alias}' to {managed_config}[/green]")
            console.print(f"[dim]Ensured {main_config} includes {managed_config}[/dim]")
            console.print(f"Use it with: ssh {shlex.quote(ssh_config_alias)}")
        else:
            console.print(entry)
        return
    if print_ssh_command:
        console.print(_shell_command(cmd))
        return
    console.print(f"[dim]Connecting to {host} via {bastion} as {login}...[/dim]")
    os.execvp("ssh", cmd)
