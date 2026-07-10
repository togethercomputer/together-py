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


def _derive(dex_url: str) -> tuple[str, str]:
    """Derive (ca_url, bastion) from the cluster's Dex issuer URL.

    A Dex issuer looks like `https://dex.<base>/<cluster-id>`, from which:
        ca_url  = https://dex.<base>/step-<cluster-id>
        bastion = ssh.<cluster-id>.<base>
    """
    u = urllib.parse.urlparse(dex_url)
    if not u.scheme or not u.hostname or not u.path.strip("/"):
        raise TogetherError("DEX_URL must look like https://dex.<base>/<cluster-id>")
    cluster_id = u.path.strip("/").split("/")[0]
    base = u.hostname[4:] if u.hostname.startswith("dex.") else u.hostname
    return f"{u.scheme}://{u.hostname}/step-{cluster_id}", f"ssh.{cluster_id}.{base}"


def _cluster_id(dex_url: str) -> str:
    u = urllib.parse.urlparse(dex_url)
    if not u.path.strip("/"):
        raise TogetherError("DEX_URL must include a cluster id path")
    return u.path.strip("/").split("/")[0]


def _redirect_uri_for_port(port: int) -> str:
    return f"http://{_DEFAULT_REDIRECT_HOST}:{port}{_DEFAULT_REDIRECT_PATH}"


def _localhost_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection((_DEFAULT_REDIRECT_HOST, port), timeout=0.2):
            return True
    except OSError:
        return False


def _callback_server(
    redirect_uri: Optional[str],
    handler: type[BaseHTTPRequestHandler],
) -> tuple[HTTPServer, str]:
    if redirect_uri is not None:
        parsed = urllib.parse.urlparse(redirect_uri)
        try:
            return HTTPServer((parsed.hostname or _DEFAULT_REDIRECT_HOST, parsed.port or 80), handler), redirect_uri
        except OSError as exc:
            raise TogetherError(f"OIDC callback port is unavailable for {redirect_uri}: {exc}") from exc

    for port in _DEFAULT_REDIRECT_PORTS:
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
        "Free one of them or pass a registered --redirect-uri."
    )


def _pkce_login(issuer: str, client_id: str, redirect_uri: Optional[str], scope: str) -> str:
    """Authorization-code + PKCE flow against Dex. Returns the raw id_token."""
    ctx = _certifi_ssl_context()
    disc = _http_json(issuer.rstrip("/") + "/.well-known/openid-configuration", ctx=ctx, purpose="OIDC discovery")
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    captured: dict[str, str] = {}

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in q:
                captured["code"] = q["code"][0]
                captured["state"] = q.get("state", [""])[0]
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

    server, redirect_uri = _callback_server(redirect_uri, _Handler)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "nonce": secrets.token_urlsafe(16),
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    auth_url = disc["authorization_endpoint"] + "?" + urllib.parse.urlencode(params)
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
        disc["token_endpoint"],
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
    with open(key_path + ".pub") as f:
        return f.read().split()[1]


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
    if os.path.exists(key_path) and os.path.exists(public_key_path):
        return _read_pubkey_blob(key_path)
    for path in (key_path, public_key_path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    return _gen_keypair(key_path, key_type)


def _read_id_token_file(path: str) -> str:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise TogetherError(f"could not securely open id token file: {path}") from exc

    with os.fdopen(fd) as f:
        file_stat = os.fstat(f.fileno())
        if not stat.S_ISREG(file_stat.st_mode):
            raise TogetherError("id token file must be a regular file")
        if file_stat.st_uid != os.geteuid():
            raise TogetherError("id token file must be owned by the current user")
        if stat.S_IMODE(file_stat.st_mode) & 0o077:
            raise TogetherError("id token file permissions are too broad; run chmod 600 on the file")
        return f.read().strip()


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


def _ssh_command(
    login: str,
    host: str,
    bastion: str,
    key_path: str,
    cert_path: str,
    known_hosts_path: str,
    ssh_args: tuple[str, ...],
) -> list[str]:
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
    return ["ssh"] + common + inner_verification + ["-o", f"ProxyCommand={proxy}", f"{login}@{host}"] + list(ssh_args)


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
    _ssh_config_value(bastion)
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
    if os.path.islink(path):
        path = os.path.realpath(path)
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


def _ensure_include(main_config_path: str, include_path: str) -> None:
    os.makedirs(os.path.dirname(main_config_path), mode=0o700, exist_ok=True)
    include_line = f"Include {_ssh_config_value(include_path)}"

    if os.path.exists(main_config_path):
        with open(main_config_path) as f:
            content = f.read()
        if any(line.strip() == include_line for line in content.splitlines()):
            return
        new_content = include_line + "\n" + content
    else:
        new_content = include_line + "\n"

    _atomic_write(main_config_path, new_content, 0o600)


def _write_ssh_config(alias: str, entry: str, cache_root: str) -> tuple[str, str]:
    managed_config = os.path.join(cache_root, "config")
    main_config = os.path.join(os.path.expanduser("~"), ".ssh", "config")
    lock_path = os.path.join(os.path.dirname(main_config), ".together-config.lock")
    os.makedirs(os.path.dirname(managed_config), mode=0o700, exist_ok=True)
    os.makedirs(os.path.dirname(lock_path), mode=0o700, exist_ok=True)

    with FileLock(lock_path, timeout=_CACHE_LOCK_TIMEOUT_SECONDS):
        if os.path.exists(managed_config):
            with open(managed_config) as f:
                content = f.read()
        else:
            content = ""

        _atomic_write(managed_config, _replace_managed_host_entry(content, alias, entry), 0o600)
        _ensure_include(main_config, managed_config)

    return managed_config, main_config


async def ssh(
    dex_url: Annotated[str, Parameter(help="Cluster Dex issuer URL: https://dex.<base>/<cluster-id>")],
    *ssh_args: Annotated[
        str,
        Parameter(allow_leading_hyphen=True, help="Extra args / remote command passed through to ssh"),
    ],
    login: Annotated[str, Parameter(name=["--login", "-l"], help="POSIX login / SSH username on the cluster")],
    host: Annotated[
        str,
        Parameter(
            help="Target host on the cluster (any hostname reachable through the bastion; e.g. slurm-login or a worker)"
        ),
    ] = "slurm-login",
    ca_url: Annotated[Optional[str], Parameter(help="Override step-ca URL (derived from DEX_URL)")] = None,
    bastion: Annotated[Optional[str], Parameter(help="Override bastion host (derived from DEX_URL)")] = None,
    client_id: Annotated[str, Parameter(help="Dex public client id")] = "together-cli",
    redirect_uri: Annotated[Optional[str], Parameter(help="OIDC redirect URI (registered on the Dex client)")] = None,
    scope: Annotated[str, Parameter(help="OIDC scopes")] = "openid email",
    key_type: Annotated[str, Parameter(help="Ephemeral key type (ecdsa is KMS-compatible)")] = "ecdsa",
    ca_root: Annotated[Optional[str], Parameter(help="step-ca root cert (PEM) for TLS")] = None,
    id_token_file: Annotated[
        Optional[str], Parameter(help="Use a pre-obtained id_token instead of the browser flow")
    ] = None,
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
    derived_ca_url, derived_bastion = _derive(dex_url)
    ca_url = ca_url or derived_ca_url
    bastion = bastion or derived_bastion
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
        os.makedirs(os.path.dirname(key_path), mode=0o700, exist_ok=True)
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
            if id_token_file:
                ott = _read_id_token_file(id_token_file)
            else:
                if cache:
                    console.print(
                        "[yellow]No valid cached SSH certificate found. Opening browser for Together login.[/yellow]"
                    )
                    console.print(
                        "[dim]Keep this terminal command running until login completes. "
                        "If you are logged out of Together Web, log in in the browser first.[/dim]"
                    )
                ott = _pkce_login(issuer, client_id, redirect_uri, scope)
            crt = _sign(ca_url, ott, pub_blob, ca_ctx)
            _atomic_write(cert_path, f"{_CERT_ALGO[key_type]} {crt} together-ssh\n", 0o644)

    known_hosts_path = os.path.join(os.path.dirname(key_path), "known_hosts")
    cmd = _ssh_command(login, host, bastion, key_path, cert_path, known_hosts_path, ssh_args)
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
