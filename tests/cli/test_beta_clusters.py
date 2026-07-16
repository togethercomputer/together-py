from __future__ import annotations

import os
import ssl
import json
import base64
import socket
import subprocess
import urllib.error
from typing import Any, cast
from http.server import BaseHTTPRequestHandler
from email.message import Message
from typing_extensions import override
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from together import TogetherError
from tests.cli.utils import CliRunner
from together.lib.cli.api.beta.clusters import ssh as ssh_cli

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _cluster_body(cluster_id: str = "cluster-1", name: str = "my-cluster", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "cluster_id": cluster_id,
        "cluster_name": name,
        "cluster_type": "KUBERNETES",
        "control_plane_nodes": [],
        "driver_version": "CUDA_12_6_565",
        "duration_hours": 24,
        "gpu_type": "H100_SXM",
        "gpu_worker_nodes": [],
        "kube_config": base64.b64encode(b"").decode("ascii"),
        "num_capacity_pool_gpus": 0,
        "num_gpus": 8,
        "num_reserved_gpus": 8,
        "region": "us-central-8",
        "status": "Ready",
        "volumes": [],
    }
    body.update(overrides)
    return body


_REGIONS_BODY = {
    "regions": [
        {
            "name": "us-central-8",
            "driver_versions": [{"cuda_version": "12.6", "nvidia_driver_version": "565"}],
            "supported_instance_types": ["H100_SXM"],
        }
    ]
}

_VOLUME_BODY = {
    "volume_id": "vol-1",
    "volume_name": "data",
    "size_tib": 2,
    "status": "available",
}


def _reserved_port() -> tuple[socket.socket, int]:
    sock = socket.socket()
    sock.bind(("localhost", 0))
    sock.listen(1)
    return sock, int(sock.getsockname()[1])


def _reserved_ipv6_port() -> tuple[socket.socket, int]:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    try:
        sock.bind(("::1", 0))
    except OSError:
        sock.close()
        pytest.skip("IPv6 loopback is unavailable")
    sock.listen(1)
    return sock, int(sock.getsockname()[1])


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.end_headers()

    @override
    def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
        pass


class TestBetaClustersSSHCallbackServer:
    def test_callback_server_skips_port_with_ipv6_listener(self, monkeypatch: pytest.MonkeyPatch) -> None:
        busy_socket, busy_port = _reserved_ipv6_port()
        free_socket, free_port = _reserved_port()
        free_socket.close()

        try:
            monkeypatch.setattr(ssh_cli, "_DEFAULT_REDIRECT_PORTS", (busy_port, free_port))

            server, redirect_uri = ssh_cli._callback_server(_CallbackHandler)
            try:
                assert redirect_uri == f"http://localhost:{free_port}/login-callback"
            finally:
                server.server_close()
        finally:
            busy_socket.close()

    def test_callback_server_uses_next_registered_port_when_first_is_busy(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        busy_socket, busy_port = _reserved_port()
        free_socket, free_port = _reserved_port()
        free_socket.close()

        try:
            monkeypatch.setattr(ssh_cli, "_DEFAULT_REDIRECT_PORTS", (busy_port, free_port))

            server, redirect_uri = ssh_cli._callback_server(_CallbackHandler)
            try:
                assert redirect_uri == f"http://localhost:{free_port}/login-callback"
            finally:
                server.server_close()
        finally:
            busy_socket.close()

    def test_callback_server_explains_when_all_registered_ports_are_busy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        first_socket, first_port = _reserved_port()
        second_socket, second_port = _reserved_port()

        try:
            monkeypatch.setattr(ssh_cli, "_DEFAULT_REDIRECT_PORTS", (first_port, second_port))

            with pytest.raises(TogetherError, match="Stop the process using one of these ports"):
                ssh_cli._callback_server(_CallbackHandler)
        finally:
            first_socket.close()
            second_socket.close()

    def test_pkce_login_explains_missing_callback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class Server:
            def handle_request(self) -> None:
                return

            def server_close(self) -> None:
                return

        def http_json(*_args: Any, **_kwargs: Any) -> dict[str, str]:
            return {
                "authorization_endpoint": "https://dex.example/auth",
                "token_endpoint": "https://dex.example/token",
            }

        def callback_server(*_args: Any, **_kwargs: Any) -> tuple[Server, str]:
            return Server(), "http://localhost:3000/login-callback"

        def open_browser(*_args: Any, **_kwargs: Any) -> bool:
            return True

        monkeypatch.setattr(ssh_cli, "_http_json", http_json)
        monkeypatch.setattr(ssh_cli, "_callback_server", callback_server)
        monkeypatch.setattr(ssh_cli.webbrowser, "open", open_browser)

        with pytest.raises(TogetherError, match="Browser login did not complete"):
            ssh_cli._pkce_login("https://dex.example/t-abc", "together-cli", "openid email")


class TestBetaClustersSSHHelpers:
    def test_callback_code_requires_registered_path_and_state(self) -> None:
        state = "expected-state"

        assert ssh_cli._callback_code(f"/login-callback?code=valid&state={state}", state) == "valid"
        assert ssh_cli._callback_code(f"/anything?code=valid&state={state}", state) is None
        assert ssh_cli._callback_code("/login-callback?code=valid&state=wrong", state) is None

    def test_validate_discovery_endpoint_accepts_trusted_origin(self) -> None:
        issuer = "https://dex.s1.cloud.together.ai/t-abc123"
        endpoint = "https://dex.s1.cloud.together.ai/t-abc123/token"

        assert ssh_cli._validate_discovery_endpoint(endpoint, issuer, "token endpoint") == endpoint

    @pytest.mark.parametrize(
        "endpoint",
        [
            "http://dex.s1.cloud.together.ai/token",
            "https://evil.example/token",
            "https://user@dex.s1.cloud.together.ai/token",
            "https://dex.s1.cloud.together.ai/token?next=evil",
        ],
    )
    def test_validate_discovery_endpoint_rejects_untrusted_origins(self, endpoint: str) -> None:
        issuer = "https://dex.s1.cloud.together.ai/t-abc123"

        with pytest.raises(TogetherError, match="trusted issuer origin"):
            ssh_cli._validate_discovery_endpoint(endpoint, issuer, "token endpoint")

    @pytest.mark.parametrize(
        "dex_url",
        [
            "http://dex.s1.cloud.together.ai/t-abc123",
            "https://dex.evil.example/t-abc123",
            "https://user@dex.s1.cloud.together.ai/t-abc123",
            "https://dex.s1.cloud.together.ai/t-abc123/extra",
            "https://dex.s1.cloud.together.ai:bad/t-abc123",
        ],
    )
    def test_derive_rejects_untrusted_dex_urls(self, dex_url: str) -> None:
        with pytest.raises(TogetherError, match="DEX_URL"):
            ssh_cli._derive(dex_url)

    def test_cache_paths_are_cluster_and_login_scoped(self, tmp_path: Any) -> None:
        key_path, cert_path = ssh_cli._cache_paths(
            "https://dex.s1.us-central-2a.cloud.together.ai/t-abc123",
            "user@example.com",
            "ecdsa",
            str(tmp_path),
        )

        assert str(tmp_path) in key_path
        assert "t-abc123-" in key_path
        assert "user%40example.com" in key_path
        assert key_path.endswith("/ecdsa/id")
        assert cert_path == key_path + "-cert.pub"

    def test_ssh_command_preserves_remote_args_and_proxy(self) -> None:
        cmd = ssh_cli._ssh_command(
            "jhu",
            "slurm-login",
            "ssh.t-abc123.s1.us-central-2a.cloud.together.ai",
            "/tmp/id",
            "/tmp/id-cert.pub",
            "/tmp/known_hosts",
            ("sinfo", "-h"),
        )

        assert cmd[:5] == ["ssh", "-i", "/tmp/id", "-o", "CertificateFile=/tmp/id-cert.pub"]
        assert "jhu@slurm-login" in cmd
        assert cmd[cmd.index("--") + 1] == "jhu@slurm-login"
        assert cmd[-2:] == ["sinfo", "-h"]
        assert any("ProxyCommand=ssh" in arg for arg in cmd)
        assert "StrictHostKeyChecking=ask" in cmd
        assert "UserKnownHostsFile=/tmp/known_hosts" in cmd
        assert "HostKeyAlias=slurm-login.ssh.t-abc123.s1.us-central-2a.cloud.together.ai" in cmd

    def test_ssh_config_entry_points_plain_ssh_at_cached_cert(self) -> None:
        entry = ssh_cli._ssh_config_entry(
            "test-oidc",
            "jhu",
            "slurm-login",
            "ssh.t-abc123.s1.us-central-2a.cloud.together.ai",
            "/home/jhu/.together/ssh/t-abc123/jhu/id",
            "/home/jhu/.together/ssh/t-abc123/jhu/id-cert.pub",
            "/home/jhu/.together/ssh/t-abc123/jhu/known_hosts",
        )

        assert "Host test-oidc" in entry
        assert "HostName slurm-login" in entry
        assert "User jhu" in entry
        assert "IdentityFile /home/jhu/.together/ssh/t-abc123/jhu/id" in entry
        assert "CertificateFile /home/jhu/.together/ssh/t-abc123/jhu/id-cert.pub" in entry
        assert "StrictHostKeyChecking ask" in entry
        assert "UserKnownHostsFile /home/jhu/.together/ssh/t-abc123/jhu/known_hosts" in entry
        assert "ProxyCommand ssh" in entry

    @pytest.mark.parametrize(
        ("login", "host", "bastion"),
        [
            ("-oProxyCommand=evil", "slurm-login", "ssh.example.com"),
            ("jhu", "slurm-login -oProxyCommand=evil", "ssh.example.com"),
            ("jhu", "slurm-login", "ssh.example.com -oProxyCommand=evil"),
            ("jhu", "slurm-login:2222", "ssh.example.com"),
            ("jhu", "slurm-login%h", "ssh.example.com"),
            ("jhu", "slurm-login", "ssh.example.com:2222"),
        ],
    )
    def test_ssh_command_rejects_invalid_destination(self, login: str, host: str, bastion: str) -> None:
        with pytest.raises(TogetherError, match="unsupported characters"):
            ssh_cli._ssh_command(
                login,
                host,
                bastion,
                "/tmp/id",
                "/tmp/id-cert.pub",
                "/tmp/known_hosts",
                (),
            )

    def test_ssh_config_entry_rejects_invalid_alias(self) -> None:
        with pytest.raises(TogetherError, match="SSH config alias"):
            ssh_cli._ssh_config_entry(
                "unsafe\nHost injected",
                "jhu",
                "slurm-login",
                "ssh.t-abc123.s1.us-central-2a.cloud.together.ai",
                "/tmp/id",
                "/tmp/id-cert.pub",
                "/tmp/known_hosts",
            )

    def test_get_or_create_keypair_replaces_partial_cache(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
        key_path = tmp_path / "id"
        key_path.write_text("partial private key")

        def generate(path: str, key_type: str) -> str:
            assert path == str(key_path)
            assert key_type == "ecdsa"
            assert not key_path.exists()
            return "new-public-key"

        monkeypatch.setattr(ssh_cli, "_gen_keypair", generate)

        assert ssh_cli._get_or_create_keypair(str(key_path), "ecdsa") == "new-public-key"

    def test_prepare_cache_directory_restricts_permissions(self, tmp_path: Any) -> None:
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(mode=0o777)
        cache_dir.chmod(0o777)

        ssh_cli._prepare_cache_directory(str(cache_dir))

        assert cache_dir.stat().st_mode & 0o777 == 0o700

    def test_read_pubkey_blob_rejects_symlink(self, tmp_path: Any) -> None:
        key_path = tmp_path / "id"
        public_key = tmp_path / "actual.pub"
        public_key.write_text("ssh-ed25519 key")
        (tmp_path / "id.pub").symlink_to(public_key)

        with pytest.raises(TogetherError, match="securely open"):
            ssh_cli._read_pubkey_blob(str(key_path))

    def test_atomic_write_replaces_symlink_without_modifying_target(self, tmp_path: Any) -> None:
        target = tmp_path / "target"
        target.write_text("original")
        link = tmp_path / "link"
        link.symlink_to(target)

        ssh_cli._atomic_write(str(link), "replacement", 0o600)

        assert not link.is_symlink()
        assert link.read_text() == "replacement"
        assert target.read_text() == "original"

    def test_replace_managed_host_entry_appends_and_updates(self) -> None:
        first = "Host test-oidc\n  HostName slurm-login\n  User jhu"
        config = ssh_cli._replace_managed_host_entry("", "test-oidc", first)
        assert config == first + "\n"

        second = "Host test-oidc\n  HostName slurm-login\n  User alice"
        config = ssh_cli._replace_managed_host_entry(config, "test-oidc", second)
        assert config == second + "\n"
        assert "User jhu" not in config

    def test_write_ssh_config_writes_managed_file_and_include(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        home = tmp_path / "home"
        cache_root = home / ".together" / "ssh"
        monkeypatch.setenv("HOME", str(home))

        entry = "Host test-oidc\n  HostName slurm-login\n  User jhu"
        managed_config, main_config = ssh_cli._write_ssh_config("test-oidc", entry, str(cache_root))

        assert managed_config == str(cache_root / "config")
        assert main_config == str(home / ".ssh" / "config")
        assert (cache_root / "config").read_text() == entry + "\n"
        assert (home / ".ssh" / "config").read_text() == f"Include {cache_root / 'config'}\n"

        ssh_cli._write_ssh_config("test-oidc", entry.replace("jhu", "alice"), str(cache_root))
        assert "User alice" in (cache_root / "config").read_text()
        assert (home / ".ssh" / "config").read_text().count("Include") == 1

    def test_write_ssh_config_quotes_paths_with_spaces(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
        home = tmp_path / "home with spaces"
        cache_root = home / ".together" / "ssh"
        monkeypatch.setenv("HOME", str(home))

        ssh_cli._write_ssh_config("test-oidc", "Host test-oidc\n  HostName slurm-login", str(cache_root))

        assert (home / ".ssh" / "config").read_text() == f'Include "{cache_root / "config"}"\n'

    def test_write_ssh_config_preserves_main_config_symlink(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        home = tmp_path / "home"
        ssh_dir = home / ".ssh"
        ssh_dir.mkdir(parents=True)
        dotfiles_config = tmp_path / "dotfiles" / "ssh-config"
        dotfiles_config.parent.mkdir()
        dotfiles_config.write_text("Host existing\n  HostName example.com\n")
        (ssh_dir / "config").symlink_to(dotfiles_config)
        monkeypatch.setenv("HOME", str(home))

        ssh_cli._write_ssh_config(
            "test-oidc",
            "Host test-oidc\n  HostName slurm-login",
            str(home / ".together" / "ssh"),
        )

        assert (ssh_dir / "config").is_symlink()
        assert "Host existing" in dotfiles_config.read_text()
        assert "Include " in dotfiles_config.read_text()

    def test_write_ssh_config_rejects_managed_config_symlink(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        home = tmp_path / "home"
        cache_root = home / ".together" / "ssh"
        cache_root.mkdir(parents=True)
        target = tmp_path / "target"
        target.write_text("Host attacker")
        (cache_root / "config").symlink_to(target)
        monkeypatch.setenv("HOME", str(home))

        with pytest.raises(TogetherError, match="managed SSH config"):
            ssh_cli._write_ssh_config("test-oidc", "Host test-oidc", str(cache_root))

        assert target.read_text() == "Host attacker"

    def test_write_ssh_config_rejects_writable_main_config_target(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        home = tmp_path / "home"
        ssh_dir = home / ".ssh"
        ssh_dir.mkdir(parents=True)
        dotfiles_config = tmp_path / "dotfiles" / "ssh-config"
        dotfiles_config.parent.mkdir()
        dotfiles_config.write_text("Host existing\n")
        dotfiles_config.chmod(0o666)
        (ssh_dir / "config").symlink_to(dotfiles_config)
        monkeypatch.setenv("HOME", str(home))

        with pytest.raises(TogetherError, match="main SSH config"):
            ssh_cli._write_ssh_config("test-oidc", "Host test-oidc", str(home / ".together" / "ssh"))

    def test_concurrent_ssh_config_writes_preserve_all_aliases(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        home = tmp_path / "home"
        cache_root = home / ".together" / "ssh"
        monkeypatch.setenv("HOME", str(home))
        aliases = [f"test-{i}" for i in range(10)]

        def write_alias(alias: str) -> None:
            ssh_cli._write_ssh_config(alias, f"Host {alias}\n  HostName slurm-login", str(cache_root))

        with ThreadPoolExecutor(max_workers=len(aliases)) as executor:
            list(executor.map(write_alias, aliases))

        content = (cache_root / "config").read_text()
        assert all(f"Host {alias}\n" in content for alias in aliases)

    def test_cert_validity_uses_ssh_keygen_expiry(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
        cert_path = tmp_path / "id-cert.pub"
        cert_path.write_text("placeholder")

        class Result:
            returncode = 0
            stdout = "        Valid: from 2026-07-09T00:00:00 to 2099-07-09T00:00:00\n"

        def run_ssh_keygen_valid(*_args: Any, **_kwargs: Any) -> Result:
            return Result()

        monkeypatch.setattr(subprocess, "run", run_ssh_keygen_valid)

        assert ssh_cli._cert_is_valid(str(cert_path)) is True

    def test_cert_validity_rejects_missing_or_expired_cert(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any
    ) -> None:
        assert ssh_cli._cert_is_valid(str(tmp_path / "missing-cert.pub")) is False

        cert_path = tmp_path / "id-cert.pub"
        cert_path.write_text("placeholder")

        class Result:
            returncode = 0
            stdout = "        Valid: from 2020-01-01T00:00:00 to 2020-01-01T01:00:00\n"

        def run_ssh_keygen_expired(*_args: Any, **_kwargs: Any) -> Result:
            return Result()

        monkeypatch.setattr(subprocess, "run", run_ssh_keygen_expired)

        assert ssh_cli._cert_is_valid(str(cert_path)) is False

    def test_cert_validity_rejects_not_yet_valid_cert(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
        cert_path = tmp_path / "id-cert.pub"
        cert_path.write_text("placeholder")

        class Result:
            returncode = 0
            stdout = "        Valid: from 2098-01-01T00:00:00 to 2099-01-01T00:00:00\n"

        def run_ssh_keygen_future(*_args: Any, **_kwargs: Any) -> Result:
            return Result()

        monkeypatch.setattr(subprocess, "run", run_ssh_keygen_future)

        assert ssh_cli._cert_is_valid(str(cert_path)) is False

    async def test_print_modes_require_cache(self) -> None:
        with pytest.raises(TogetherError, match="require cached"):
            await ssh_cli.ssh(
                "https://dex.s1.us-central-2a.cloud.together.ai/t-abc123",
                login="jhu",
                cache=False,
                print_ssh_command=True,
            )

    async def test_write_ssh_config_requires_alias(self) -> None:
        with pytest.raises(TogetherError, match="requires --ssh-config-alias"):
            await ssh_cli.ssh(
                "https://dex.s1.us-central-2a.cloud.together.ai/t-abc123",
                login="jhu",
                write_ssh_config=True,
            )

    def test_http_json_404_mentions_oidc_endpoint_and_cli_upgrade(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def raise_404(*_args: Any, **_kwargs: Any) -> None:
            raise urllib.error.HTTPError(
                url="https://dex.example/t-abc/.well-known/openid-configuration",
                code=404,
                msg="Not Found",
                hdrs=Message(),
                fp=None,
            )

        monkeypatch.setattr(ssh_cli.urllib.request, "urlopen", raise_404)

        with pytest.raises(TogetherError, match="OIDC discovery failed"):
            ssh_cli._http_json("https://dex.example/t-abc/.well-known/openid-configuration", purpose="OIDC discovery")

    def test_http_json_tls_error_suggests_certifi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def raise_tls(*_args: Any, **_kwargs: Any) -> None:
            raise urllib.error.URLError("CERTIFICATE_VERIFY_FAILED")

        monkeypatch.setattr(ssh_cli.urllib.request, "urlopen", raise_tls)

        with pytest.raises(TogetherError, match="bundled CA store"):
            ssh_cli._http_json("https://dex.example/t-abc/.well-known/openid-configuration", purpose="OIDC discovery")

    def test_sign_tls_error_suggests_certifi(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def raise_tls(*_args: Any, **_kwargs: Any) -> None:
            raise urllib.error.URLError("CERTIFICATE_VERIFY_FAILED")

        monkeypatch.setattr(ssh_cli.urllib.request, "urlopen", raise_tls)

        with pytest.raises(TogetherError, match="ca-root"):
            ssh_cli._sign("https://dex.example/step-t-abc", "ott", "pub", None)

    def test_certifi_ssl_context_ignores_broken_ssl_cert_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SSL_CERT_FILE", "/does/not/exist")

        assert isinstance(ssh_cli._certifi_ssl_context(), ssl.SSLContext)


def _remediation_body(remediation_id: str = "rem-1", **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": remediation_id,
        "cluster_id": "c1",
        "instance_id": "i1",
        "mode": "REMEDIATION_MODE_VM_ONLY",
        "state": "PENDING_APPROVAL",
        "trigger": "REMEDIATION_TRIGGER_AUTOMATED",
        "reason": "health check failed",
    }
    body.update(overrides)
    return body


def _remediation_list_body(*remediations: dict[str, Any]) -> dict[str, Any]:
    return {
        "has_next": False,
        "next_page_token": "",
        "remediations": list(remediations),
    }


class TestBetaClustersList:
    @pytest.mark.respx(base_url=base_url)
    def test_list_table(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(
                200,
                json={"clusters": [_cluster_body("a", "alpha"), _cluster_body("b", "beta")]},
            )
        )
        result = cli_runner.invoke(["beta", "clusters", "list"])
        assert "a" in result.output
        assert "alpha" in result.output
        assert "b" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = {"clusters": [_cluster_body()]}
        respx_mock.get("/compute/clusters").mock(return_value=httpx.Response(200, json=payload))
        result = cli_runner.invoke(["beta", "clusters", "list", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0


class TestBetaClustersListRegions:
    @pytest.mark.respx(base_url=base_url)
    def test_list_regions_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/regions").mock(return_value=httpx.Response(200, json=_REGIONS_BODY))
        result = cli_runner.invoke(["beta", "clusters", "list-regions", "--json"])
        assert json.loads(result.output) == _REGIONS_BODY
        assert result.exit_code == 0


class TestBetaClustersRetrieve:
    @pytest.mark.respx(base_url=base_url)
    def test_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        c = _cluster_body()
        respx_mock.get("/compute/clusters/cluster-1").mock(return_value=httpx.Response(200, json=c))
        result = cli_runner.invoke(["beta", "clusters", "retrieve", "cluster-1", "--json"])
        assert json.loads(result.output) == c
        assert result.exit_code == 0


class TestBetaClustersCreate:
    @pytest.mark.respx(base_url=base_url)
    def test_create_non_interactive_posts_expected_body(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        created = _cluster_body("new-id", "together-py-testing-suite")
        route = respx_mock.post("/compute/clusters").mock(return_value=httpx.Response(200, json=created))
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "create",
                "--non-interactive",
                "--cluster-type",
                "KUBERNETES",
                "--gpu-type",
                "H100_SXM",
                "--nvidia-driver-version",
                "565",
                "--cuda-version",
                "12.6",
                "--region",
                "us-central-8",
                "--num-gpus",
                "8",
                "--billing-type",
                "ON_DEMAND",
                "--name",
                "together-py-testing-suite",
                "--volume",
                "vol-attach",
            ],
        )
        assert "new-id" in result.output
        raw = cast(Call, route.calls[0]).request.content.decode()
        body = json.loads(raw)
        assert body["cluster_name"] == "together-py-testing-suite"
        assert body["volume_id"] == "vol-attach"
        assert body["num_gpus"] == 8
        assert body["billing_type"] == "ON_DEMAND"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_create_accepts_new_cluster_params(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        created = _cluster_body("new-id", "scheduled")
        route = respx_mock.post("/compute/clusters").mock(return_value=httpx.Response(200, json=created))
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "create",
                "--non-interactive",
                "--cluster-type",
                "SLURM",
                "--gpu-type",
                "H100_SXM",
                "--nvidia-driver-version",
                "565",
                "--cuda-version",
                "12.6",
                "--region",
                "us-central-8",
                "--num-gpus",
                "8",
                "--billing-type",
                "SCHEDULED_CAPACITY",
                "--name",
                "scheduled",
                "--auto-scale",
                "--auto-scale-max-gpus",
                "16",
                "--capacity-pool-id",
                "pool-1",
                "--install-traefik",
                "--num-capacity-pool-gpus",
                "8",
                "--num-preemptible-gpus",
                "8",
                "--num-reserved-gpus",
                "8",
                "--project",
                "proj-1",
                "--reservation-start-time",
                "2026-06-01T00:00:00Z",
                "--reservation-end-time",
                "2026-06-02T00:00:00Z",
                "--slurm-image",
                "slurm:latest",
                "--slurm-shm-size-gib",
                "32",
            ],
        )

        assert result.exit_code == 0, result.output
        body = json.loads(cast(Call, route.calls[0]).request.content.decode())
        assert body["billing_type"] == "SCHEDULED_CAPACITY"
        assert body["auto_scale"] is True
        assert body["auto_scale_max_gpus"] == 16
        assert body["capacity_pool_id"] == "pool-1"
        assert "gpu_node_failover_enabled" not in body
        assert body["install_traefik"] is True
        assert body["num_capacity_pool_gpus"] == 8
        assert body["num_preemptible_gpus"] == 8
        assert body["num_reserved_gpus"] == 8
        assert body["project_id"] == "proj-1"
        assert body["reservation_start_time"] == "2026-06-01T00:00:00Z"
        assert body["reservation_end_time"] == "2026-06-02T00:00:00Z"
        assert body["slurm_image"] == "slurm:latest"
        assert body["slurm_shm_size_gib"] == 32
        assert result.exit_code == 0


class TestBetaClustersUpdate:
    @pytest.mark.respx(base_url=base_url)
    def test_update_json_triggers_put_and_second_get(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        updated = _cluster_body("c1", num_gpus=16, cluster_type="SLURM")
        put = respx_mock.put("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        get = respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        result = cli_runner.invoke(
            ["beta", "clusters", "update", "c1", "--num-gpus", "16", "--cluster-type", "SLURM", "--json"],
        )
        assert put.calls
        assert get.calls
        assert json.loads(result.output)["num_gpus"] == 16
        put_body = json.loads(cast(Call, put.calls[0]).request.content.decode())
        assert put_body["num_gpus"] == 16
        assert put_body["cluster_type"] == "SLURM"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_update_accepts_new_cluster_params(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        updated = _cluster_body("c1", num_gpus=16)
        put = respx_mock.put("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=updated))
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "update",
                "c1",
                "--num-preemptible-gpus",
                "8",
                "--num-capacity-pool-gpus",
                "8",
                "--num-reserved-gpus",
                "16",
                "--reservation-end-time",
                "2026-06-02T00:00:00Z",
            ],
        )

        put_body = json.loads(cast(Call, put.calls[0]).request.content.decode())
        assert put_body["num_preemptible_gpus"] == 8
        assert put_body["num_capacity_pool_gpus"] == 8
        assert put_body["num_reserved_gpus"] == 16
        assert put_body["reservation_end_time"] == "2026-06-02T00:00:00Z"
        assert result.exit_code == 0


class TestBetaClustersDelete:
    @pytest.mark.respx(base_url=base_url)
    def test_delete_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/compute/clusters/c-del").mock(
            return_value=httpx.Response(200, json={"cluster_id": "c-del"})
        )
        result = cli_runner.invoke(["beta", "clusters", "delete", "c-del", "--json"])
        assert json.loads(result.output) == {"cluster_id": "c-del"}
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_delete_confirm_yes(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        c = _cluster_body("c1", "to-delete")
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        respx_mock.delete("/compute/clusters/c1").mock(return_value=httpx.Response(200, json={"cluster_id": "c1"}))
        result = cli_runner.invoke(["beta", "clusters", "delete", "c1"], input="y\n")
        assert "Deleted" in result.output
        assert result.exit_code == 0


class TestBetaClustersGetCredentials:
    @pytest.mark.respx(base_url=base_url)
    def test_get_credentials_stdout(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        cfg = "apiVersion: v1\nkind: Config\n"
        c = _cluster_body(kube_config=base64.b64encode(cfg.encode()).decode("ascii"))
        respx_mock.get("/compute/clusters/c1").mock(return_value=httpx.Response(200, json=c))
        result = cli_runner.invoke(["beta", "clusters", "get-credentials", "c1", "--file", "-"])
        assert result.output.strip() == cfg.strip()
        assert result.exit_code == 0


class TestBetaClustersStorage:
    @pytest.mark.respx(base_url=base_url)
    def test_storage_list_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = {"volumes": [_VOLUME_BODY]}
        respx_mock.get("/compute/clusters/storage/volumes").mock(return_value=httpx.Response(200, json=payload))
        result = cli_runner.invoke(["beta", "clusters", "storage", "list", "--json"])
        assert json.loads(result.output) == payload
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_create_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/compute/clusters/storage/volumes").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "storage",
                "create",
                "--region",
                "us-east-1",
                "--size-tib",
                "1",
                "--volume-name",
                "test-volume",
                "--is-lifecycle-independent",
                "--json",
            ],
        )
        out = json.loads(result.output)
        assert out["volume_id"] == "vol-1"
        raw = cast(Call, route.calls[0]).request.content.decode()
        assert json.loads(raw) == {
            "region": "us-east-1",
            "size_tib": 1,
            "volume_name": "test-volume",
            "is_lifecycle_independent": True,
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_update_allows_omitting_size(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.put("/compute/clusters/storage/volumes").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "update", "vol-1", "--json"])

        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {"volume_id": "vol-1"}
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_retrieve_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.get("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json=_VOLUME_BODY)
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "retrieve", "vol-1", "--json"])
        assert json.loads(result.output) == _VOLUME_BODY
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_storage_delete_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        respx_mock.delete("/compute/clusters/storage/volumes/vol-1").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        result = cli_runner.invoke(["beta", "clusters", "storage", "delete", "vol-1", "--json"])
        assert json.loads(result.output) == {"success": True}
        assert result.exit_code == 0


class TestBetaClustersRemediations:
    @pytest.mark.respx(base_url=base_url)
    def test_remediations_create_json(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-created", state="PENDING"))
        )
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "create",
                "c1",
                "i1",
                "--mode",
                "VM_ONLY",
                "--reason",
                "node unhealthy",
                "--remediation-id",
                "rem-created",
                "--json",
            ],
        )

        assert json.loads(result.output)["id"] == "rem-created"
        request = cast(Call, route.calls[0]).request
        assert request.url.params["remediation_id"] == "rem-created"
        assert json.loads(request.content.decode()) == {
            "mode": "REMEDIATION_MODE_VM_ONLY",
            "reason": "node unhealthy",
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_uses_wildcard_when_instance_id_omitted(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1", "--json"])

        assert json.loads(result.output) == payload
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/-/remediations"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_accepts_instance_id(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/i1/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1", "i1", "--json"])

        assert json.loads(result.output) == payload
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/i1/remediations"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_table_uses_instance_name(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body(instance_name="gpu-node-a"))
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1"])

        assert "gpu-node-a (i1)" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_table_falls_back_to_instance_id(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        payload = _remediation_list_body(_remediation_body())
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "list", "c1"])

        assert "i1" in result.output
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_list_accepts_filters(self, respx_mock: MockRouter, cli_runner: CliRunner) -> None:
        payload = _remediation_list_body(_remediation_body())
        route = respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=payload)
        )
        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "list",
                "c1",
                "--mode",
                "VM_ONLY",
                "--mode",
                "REBOOT_VM",
                "--state",
                "PENDING_APPROVAL",
                "--trigger",
                "AUTOMATED",
                "--after",
                "next-token",
                "--json",
            ]
        )

        params = cast(Call, route.calls[0]).request.url.params
        assert params["mode"] == "REMEDIATION_MODE_VM_ONLY,REMEDIATION_MODE_REBOOT_VM"
        assert params["state"] == "PENDING_APPROVAL"
        assert params["trigger"] == "REMEDIATION_TRIGGER_AUTOMATED"
        assert params["page_token"] == "next-token"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_retrieve_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        body = _remediation_body("rem-get", state="RUNNING")
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-get")))
        )
        route = respx_mock.get("/compute/clusters/c1/instances/i1/remediations/rem-get").mock(
            return_value=httpx.Response(200, json=body)
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "get", "rem-get", "--json"])

        assert json.loads(result.output) == body
        assert cast(Call, route.calls[0]).request.url.path == "/compute/clusters/c1/instances/i1/remediations/rem-get"
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_approve_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-approve")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-approve/approve").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-approve", state="PENDING"))
        )

        result = cli_runner.invoke(
            [
                "beta",
                "clusters",
                "remediations",
                "approve",
                "rem-approve",
                "--comment",
                "go",
                "--mode",
                "REBOOT_VM",
                "--json",
            ]
        )

        assert json.loads(result.output)["state"] == "PENDING"
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {
            "comment": "go",
            "mode": "REMEDIATION_MODE_REBOOT_VM",
        }
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_cancel_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-cancel")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-cancel/cancel").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-cancel", state="CANCELLED"))
        )

        result = cli_runner.invoke(["beta", "clusters", "remediations", "cancel", "rem-cancel", "--json"])

        assert json.loads(result.output)["state"] == "CANCELLED"
        assert route.calls
        assert result.exit_code == 0

    @pytest.mark.respx(base_url=base_url)
    def test_remediations_reject_resolves_cluster_and_instance(
        self, respx_mock: MockRouter, cli_runner: CliRunner
    ) -> None:
        respx_mock.get("/compute/clusters").mock(
            return_value=httpx.Response(200, json={"clusters": [_cluster_body("c1")]})
        )
        respx_mock.get("/compute/clusters/c1/instances/-/remediations").mock(
            return_value=httpx.Response(200, json=_remediation_list_body(_remediation_body("rem-reject")))
        )
        route = respx_mock.post("/compute/clusters/c1/instances/i1/remediations/rem-reject/reject").mock(
            return_value=httpx.Response(200, json=_remediation_body("rem-reject", state="CANCELLED"))
        )

        result = cli_runner.invoke(
            ["beta", "clusters", "remediations", "reject", "rem-reject", "--comment", "skip", "--json"]
        )

        assert json.loads(result.output)["state"] == "CANCELLED"
        assert json.loads(cast(Call, route.calls[0]).request.content.decode()) == {"comment": "skip"}
        assert result.exit_code == 0
