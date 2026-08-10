"""Unit tests for `tg login` OIDC credential storage and invisible refresh."""

from __future__ import annotations

import json
import time
from typing import Any
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from together import TogetherError
from together.lib.cli.auth import oidc as oidc_mod, credentials as creds_mod


@pytest.fixture(autouse=True)
def _isolated_credentials(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(path))
    monkeypatch.delenv("TOGETHER_OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("TOGETHER_OAUTH_CLIENT_SECRET", raising=False)
    return path


def _stored(**overrides: Any) -> creds_mod.StoredCredentials:
    base: dict[str, Any] = {
        "access_token": "access-1",
        "refresh_token": "refresh-1",
        "expires_at": time.time() + 300,
        "client_id": "app_cli",
        "token_endpoint": "https://api.together.ai/oauth/token",
        "issuer": "https://ums.together.ai",
        "scope": "openid email profile",
    }
    base.update(overrides)
    return creds_mod.StoredCredentials(**base)


class TestCredentialsStore:
    def test_save_load_roundtrip(self) -> None:
        original = _stored()
        path = creds_mod.save_credentials(original)
        assert path.is_file()
        loaded = creds_mod.load_credentials()
        assert loaded is not None
        assert loaded.access_token == "access-1"
        assert loaded.refresh_token == "refresh-1"
        assert loaded.client_id == "app_cli"
        raw = json.loads(path.read_text())
        assert "access_token" in raw

    def test_clear_credentials(self) -> None:
        creds_mod.save_credentials(_stored())
        assert creds_mod.clear_credentials() is True
        assert creds_mod.load_credentials() is None
        assert creds_mod.clear_credentials() is False


class TestDiscoveryHelpers:
    def test_discovery_url_from_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
        assert oidc_mod.discovery_url_from_base_url() == ("https://api.together.ai/.well-known/openid-configuration")

    def test_discovery_url_strips_v1(self) -> None:
        assert oidc_mod.discovery_url_from_base_url("https://api.qa.together.ai/v1") == (
            "https://api.qa.together.ai/.well-known/openid-configuration"
        )


class TestTokenRefresh:
    def test_resolve_returns_valid_token_without_refresh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        creds_mod.save_credentials(_stored(expires_at=time.time() + 120))

        def boom(*_a: object, **_k: object) -> Any:
            raise AssertionError("should not refresh")

        monkeypatch.setattr(oidc_mod, "refresh_access_token", boom)
        assert oidc_mod.resolve_access_token() == "access-1"

    def test_resolve_refreshes_near_expiry(self, monkeypatch: pytest.MonkeyPatch) -> None:
        creds_mod.save_credentials(_stored(expires_at=time.time() + 5))

        def fake_refresh(_credentials: creds_mod.StoredCredentials, **_k: object) -> creds_mod.StoredCredentials:
            refreshed = _stored(access_token="access-2", expires_at=time.time() + 300)
            creds_mod.save_credentials(refreshed)
            return refreshed

        monkeypatch.setattr(oidc_mod, "refresh_access_token", fake_refresh)
        assert oidc_mod.resolve_access_token() == "access-2"
        loaded = creds_mod.load_credentials()
        assert loaded is not None
        assert loaded.access_token == "access-2"

    def test_refresh_posts_refresh_token_grant(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stored = _stored(expires_at=time.time() - 1)
        creds_mod.save_credentials(stored)
        captured: dict[str, Any] = {}

        def fake_http_json(url: str, data: dict[str, Any] | None = None, **_k: object) -> dict[str, Any]:
            captured["url"] = url
            captured["data"] = data
            return {
                "access_token": "access-new",
                "refresh_token": "refresh-new",
                "expires_in": 300,
                "token_type": "Bearer",
            }

        monkeypatch.setattr(oidc_mod, "_http_json", fake_http_json)
        monkeypatch.setenv("TOGETHER_OAUTH_CLIENT_SECRET", "sekrit")

        refreshed = oidc_mod.refresh_access_token(stored)
        assert refreshed.access_token == "access-new"
        assert captured["url"] == "https://api.together.ai/oauth/token"
        assert captured["data"]["grant_type"] == "refresh_token"
        assert captured["data"]["refresh_token"] == "refresh-1"
        assert captured["data"]["client_id"] == "app_cli"
        assert captured["data"]["client_secret"] == "sekrit"
        loaded = creds_mod.load_credentials()
        assert loaded is not None
        assert loaded.access_token == "access-new"

    def test_login_requires_client_id(self) -> None:
        with pytest.raises(TogetherError, match="client_id"):
            oidc_mod.login_with_oidc(client_id=None)

    def test_resolve_returns_none_when_refresh_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        creds_mod.save_credentials(_stored(expires_at=time.time() - 1))

        def fail_refresh(*_a: object, **_k: object) -> creds_mod.StoredCredentials:
            raise TogetherError("refresh failed")

        monkeypatch.setattr(oidc_mod, "refresh_access_token", fail_refresh)
        assert oidc_mod.resolve_access_token() is None


class TestLoginFlow:
    def test_pkce_login_exchanges_code(self, monkeypatch: pytest.MonkeyPatch) -> None:
        disc = {
            "issuer": "https://ums.together.ai",
            "authorization_endpoint": "https://api.together.ai/oauth/authorize",
            "token_endpoint": "https://api.together.ai/oauth/token",
        }
        monkeypatch.setattr(oidc_mod, "fetch_openid_configuration", lambda *_a, **_k: disc)
        monkeypatch.setattr(oidc_mod, "_pkce_pair", lambda: ("v" * 43, "challenge"))
        monkeypatch.setattr(oidc_mod.secrets, "token_urlsafe", lambda *_a, **_k: "fixed-state")
        monkeypatch.setattr(oidc_mod.webbrowser, "open", lambda _url: True)

        def fake_callback_server(handler_cls: type) -> tuple[Any, str]:
            server = MagicMock()
            redirect = "http://localhost:3000/login-callback"

            def handle_request() -> None:
                handler = handler_cls.__new__(handler_cls)
                handler.path = "/login-callback?code=auth-code&state=fixed-state"
                handler.send_response = MagicMock()
                handler.end_headers = MagicMock()
                handler.wfile = MagicMock()
                handler.wfile.write = MagicMock()
                handler.do_GET()

            server.handle_request.side_effect = handle_request
            server.server_close = MagicMock()
            return server, redirect

        monkeypatch.setattr(oidc_mod, "_callback_server", fake_callback_server)

        token_calls: list[dict[str, Any]] = []

        def fake_http_json(url: str, data: dict[str, Any] | None = None, **_k: object) -> dict[str, Any]:
            token_calls.append({"url": url, "data": data})
            return {
                "access_token": "access-login",
                "refresh_token": "refresh-login",
                "expires_in": 300,
                "id_token": "id-login",
                "token_type": "Bearer",
                "scope": "openid email profile",
            }

        monkeypatch.setattr(oidc_mod, "_http_json", fake_http_json)

        credentials = oidc_mod.login_with_oidc(client_id="app_cli", client_secret="sekrit", open_browser=False)
        assert credentials.access_token == "access-login"
        assert credentials.refresh_token == "refresh-login"
        assert token_calls[0]["data"]["grant_type"] == "authorization_code"
        assert token_calls[0]["data"]["code"] == "auth-code"
        assert token_calls[0]["data"]["code_verifier"] == "v" * 43
        assert token_calls[0]["data"]["client_secret"] == "sekrit"
        loaded = creds_mod.load_credentials()
        assert loaded is not None
        assert loaded.access_token == "access-login"


class TestCliNoAuthLogin:
    def test_login_command_does_not_require_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import together.lib.cli as cli

        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        monkeypatch.setenv("TOGETHER_DISABLE_VERSION_CHECK", "1")
        monkeypatch.setenv("TOGETHER_OAUTH_CLIENT_ID", "app_cli")

        require_flags: list[bool] = []
        resolve_calls = 0
        real_create = cli._create_client

        def spy_create(*args: object, require_api_key: bool = True, **kwargs: object):  # type: ignore[no-untyped-def]
            require_flags.append(require_api_key)
            return real_create(*args, require_api_key=require_api_key, **kwargs)  # type: ignore[arg-type]

        async def spy_resolve(_client: object) -> str:
            nonlocal resolve_calls
            resolve_calls += 1
            return "proj"

        def fake_login_with_oidc(**_k: object) -> creds_mod.StoredCredentials:
            return _stored()

        monkeypatch.setattr(cli, "_create_client", spy_create)
        monkeypatch.setattr(cli, "_resolve_project_id", spy_resolve)
        monkeypatch.setattr("together.lib.cli.api.login.login_with_oidc", fake_login_with_oidc)

        try:
            cli.app.meta(["login", "--no-browser"])
        except SystemExit:
            pass

        assert require_flags == [False]
        assert resolve_calls == 0

    def test_resolve_cli_api_key_uses_oidc(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import together.lib.cli as cli

        monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
        creds_mod.save_credentials(_stored(expires_at=time.time() + 120))
        assert cli._resolve_cli_api_key(None) == "access-1"

    def test_resolve_cli_api_key_prefers_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import together.lib.cli as cli

        monkeypatch.setenv("TOGETHER_API_KEY", "env-key")
        creds_mod.save_credentials(_stored())
        assert cli._resolve_cli_api_key(None) == "env-key"
        assert cli._resolve_cli_api_key("flag-key") == "flag-key"
