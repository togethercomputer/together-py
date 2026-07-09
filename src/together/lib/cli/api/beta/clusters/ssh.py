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
import ssl
import json as json_lib
import base64
import socket
import hashlib
import secrets
import tempfile
import subprocess
import webbrowser
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional, Annotated, cast
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

from cyclopts import Parameter

from together import TogetherError
from together.lib.cli.utils._console import console

_CERT_ALGO = {
    "ecdsa": "ecdsa-sha2-nistp256-cert-v01@openssh.com",
    "ed25519": "ssh-ed25519-cert-v01@openssh.com",
}
_DEFAULT_REDIRECT_HOST = "localhost"
_DEFAULT_REDIRECT_PATH = "/login-callback"
_DEFAULT_REDIRECT_PORTS = (3000, 10001, 11110)


def _http_json(
    url: str,
    data: Optional[dict[str, Any]] = None,
    ctx: Optional[ssl.SSLContext] = None,
) -> dict[str, Any]:
    """GET (data=None) or form-POST JSON helper using stdlib only."""
    if data is None:
        req = urllib.request.Request(url, method="GET")
    else:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, context=ctx) as resp:
        return cast("dict[str, Any]", json_lib.loads(resp.read().decode()))


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
    disc = _http_json(issuer.rstrip("/") + "/.well-known/openid-configuration")
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
        raise TogetherError("OIDC login failed (no code or state mismatch)")
    tok = _http_json(
        disc["token_endpoint"],
        data={
            "grant_type": "authorization_code",
            "code": captured["code"],
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": verifier,
        },
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
        raise TogetherError(f"step-ca /ssh/sign failed ({e.code}): {e.read().decode()[:300]}") from e
    if "crt" not in out:
        raise TogetherError(f"step-ca returned no crt: {out}")
    return str(out["crt"])


def _gen_keypair(tmpdir: str, key_type: str) -> tuple[str, str]:
    """ssh-keygen an ephemeral keypair. Returns (key_path, pubkey_blob)."""
    key_path = os.path.join(tmpdir, "id")
    subprocess.run(
        ["ssh-keygen", "-t", key_type, "-f", key_path, "-N", "", "-q", "-C", "together-ssh"],
        check=True,
    )
    with open(key_path + ".pub") as f:
        return key_path, f.read().split()[1]


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
    insecure: Annotated[bool, Parameter(negative=False, help="Skip step-ca TLS verification")] = False,
    id_token_file: Annotated[
        Optional[str], Parameter(help="Use a pre-obtained id_token instead of the browser flow")
    ] = None,
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

    if insecure:
        ca_ctx: Optional[ssl.SSLContext] = ssl._create_unverified_context()
    elif ca_root:
        ca_ctx = ssl.create_default_context(cafile=ca_root)
    else:
        ca_ctx = None

    if id_token_file:
        with open(id_token_file) as f:
            ott = f.read().strip()
    else:
        ott = _pkce_login(issuer, client_id, redirect_uri, scope)

    with tempfile.TemporaryDirectory(prefix="together-ssh-") as tmp:
        key_path, pub_blob = _gen_keypair(tmp, key_type)
        crt = _sign(ca_url, ott, pub_blob, ca_ctx)
        cert_path = key_path + "-cert.pub"
        with open(cert_path, "w") as f:
            f.write(f"{_CERT_ALGO[key_type]} {crt} together-ssh\n")

        common = ["-i", key_path, "-o", f"CertificateFile={cert_path}", "-o", "IdentitiesOnly=yes"]
        # Bastion hop is the internet-facing edge and its hostname is unique per
        # cluster, so it keeps normal host-key verification (proxy uses `common`
        # only). The inner hop runs through the bastion, already inside the
        # cluster, and targets generic names (slurm-login, workers) whose host
        # keys both churn on pod restarts and collide across clusters. Skip
        # host-key checking on that inner hop only.
        proxy = "ssh " + " ".join(common) + f" -W %h:%p {login}@{bastion}"
        inner_insecure = ["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"]
        cmd = ["ssh"] + common + inner_insecure + ["-o", f"ProxyCommand={proxy}", f"{login}@{host}"] + list(ssh_args)
        console.print(f"[dim]Connecting to {host} via {bastion} as {login}...[/dim]")
        os.execvp("ssh", cmd)
