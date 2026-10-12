from __future__ import annotations

import os
import json
from typing import Any
from pathlib import Path

import httpx
import pytest
from respx import MockRouter

from together import TogetherError
from tests.cli.utils import CliRunner, patch_httpx_client
from together.lib.cli import auth
from together.lib.cli.auth import (
    DeviceCode,
    TogetherAuth,
    CredentialStore,
    StoredCredentials,
    credentials_path,
    load_stored_credentials,
    save_stored_credentials,
)


def _discovery(**overrides: Any) -> dict[str, Any]:
    body = {
        "issuer": "https://ums.together.ai",
        "authorization_endpoint": "https://api.together.ai/oauth/authorize",
        "token_endpoint": "https://api.together.ai/v1/auth/token",
        "device_authorization_endpoint": "https://api.together.ai/v1/auth/device/code",
        "grant_types_supported": [
            "authorization_code",
            "urn:ietf:params:oauth:grant-type:device_code",
        ],
    }
    body.update(overrides)
    return body


def _device_auth(**overrides: Any) -> dict[str, Any]:
    body = {
        "device_code": "odc_v1_device",
        "user_code": "BCDF-GHJK",
        "verification_uri": "https://api.together.ai/login/device",
        "verification_uri_complete": "https://api.together.ai/login/device?user_code=BCDF-GHJK",
        "expires_in": 600,
        "interval": 1,
    }
    body.update(overrides)
    return body


@pytest.fixture
def creds_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(path))
    return path


def test_discover_requires_device_endpoint() -> None:
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            json={"issuer": "https://ums.together.ai", "token_endpoint": "https://api.together.ai/oauth/token"},
        )
    )
    with httpx.Client(transport=transport) as client:
        with pytest.raises(TogetherError, match="device_authorization_endpoint"):
            auth._OIDCClient(client, "https://api.together.ai").discover(require_device=True)


def test_validate_discovery_rejects_off_host() -> None:
    with pytest.raises(TogetherError, match="together.ai host"):
        auth._validate_endpoint(
            "https://evil.example/device",
            "https://api.together.ai",
            "device authorization endpoint",
        )


def _staging_discovery(**overrides: Any) -> dict[str, Any]:
    body = {
        "issuer": "https://ums.together.ai",
        "authorization_endpoint": "https://staging.together.ai/oauth/authorize",
        "token_endpoint": "https://staging.together.ai/oauth/token",
        "device_authorization_endpoint": "https://staging.together.ai/login/oauth/device-authorization",
        "grant_types_supported": [
            "authorization_code",
            "urn:ietf:params:oauth:grant-type:device_code",
        ],
    }
    body.update(overrides)
    return body


@pytest.mark.usefixtures("creds_file")
def test_device_login_uses_the_hardcoded_cli_client_id() -> None:
    posted: dict[str, str] = {}
    polled: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            # A client id advertised in discovery is ignored.
            return httpx.Response(200, json={**_staging_discovery(), "together_cli_client_id": "app_advertised"})
        if path.endswith("/login/oauth/device-authorization"):
            assert request.method == "POST"
            assert request.headers["content-type"] == "application/x-www-form-urlencoded"
            form = dict(httpx.QueryParams(request.content.decode()))
            posted.update(form)
            return httpx.Response(
                200,
                json=_device_auth(
                    verification_uri="https://staging.together.ai/login/device",
                    verification_uri_complete="https://staging.together.ai/login/device?code=BCDF-GHJK",
                ),
            )
        if path.endswith("/oauth/token"):
            polled.update(dict(httpx.QueryParams(request.content.decode())))
            return httpx.Response(200, json={"access_token": "jwt-access", "token_type": "Bearer"})
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        tokens = TogetherAuth(http_client=client).login(
            "https://staging.together.ai", on_prompt=lambda _code: None, sleep=lambda _s: None, monotonic=lambda: 0.0
        )

    assert auth.CLI_CLIENT_ID == "app_CfXyxzEgNqQmH1PJEr2Xw"
    assert posted["client_id"] == "app_CfXyxzEgNqQmH1PJEr2Xw"
    assert polled["client_id"] == "app_CfXyxzEgNqQmH1PJEr2Xw"
    assert tokens.client_id == "app_CfXyxzEgNqQmH1PJEr2Xw"
    stored = load_stored_credentials()
    assert stored is not None and stored.client_id == "app_CfXyxzEgNqQmH1PJEr2Xw"


def test_device_login_plaintext_token(
    creds_file: Path,
) -> None:
    polls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/v1/auth/device/code"):
            form = dict(httpx.QueryParams(request.content.decode()))
            # Only the client id is sent; no public key for response encryption.
            assert form == {"client_id": auth.CLI_CLIENT_ID}
            return httpx.Response(200, json=_device_auth())
        if path.endswith("/v1/auth/token"):
            polls["n"] += 1
            if polls["n"] == 1:
                return httpx.Response(400, json={"error": "authorization_pending"})
            if polls["n"] == 2:
                return httpx.Response(400, json={"error": "slow_down", "interval": 2})
            return httpx.Response(
                200,
                json={
                    "access_token": "jwt-access",
                    "token_type": "Bearer",
                    "refresh_token": "rt-1",
                    "expires_in": 3600,
                },
            )
        return httpx.Response(404)

    prompts: list[DeviceCode] = []
    sleeps: list[float] = []
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        tokens = TogetherAuth(http_client=client).login(
            "https://api.together.ai", on_prompt=prompts.append, sleep=sleeps.append, monotonic=lambda: 0.0
        )

    assert tokens.access_token == "jwt-access"
    assert tokens.refresh_token == "rt-1"
    assert credentials_path() == creds_file
    assert prompts == [
        DeviceCode(
            user_code="BCDF-GHJK",
            verification_uri="https://api.together.ai/login/device",
            browser_url="https://api.together.ai/login/device?user_code=BCDF-GHJK",
        )
    ]
    assert sleeps == [1, 2]
    stored = load_stored_credentials()
    assert stored is not None
    assert stored.access_token == "jwt-access"


@pytest.mark.usefixtures("creds_file")
def test_device_login_rejects_encrypted_token_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/v1/auth/device/code"):
            return httpx.Response(200, json=_device_auth(interval=1))
        return httpx.Response(200, json={"response": "eyJhbGciOiJFQ0RILUVTK0EyNTZLVyJ9.a.b.c.d"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(TogetherError, match="encrypted response"):
            TogetherAuth(http_client=client).login(
                "https://api.together.ai", on_prompt=lambda _code: None, sleep=lambda _s: None, monotonic=lambda: 0.0
            )


@pytest.mark.parametrize(
    ("error", "match"),
    [
        ("access_denied", "denied"),
        ("expired_token", "expired"),
        ("invalid_grant", "could not be completed"),
    ],
)
def test_device_login_terminal_errors(error: str, match: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/v1/auth/device/code"):
            return httpx.Response(200, json=_device_auth(interval=1))
        return httpx.Response(400, json={"error": error})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(TogetherError, match=match):
            TogetherAuth(http_client=client).login(
                "https://api.together.ai", on_prompt=lambda _code: None, sleep=lambda _s: None, monotonic=lambda: 0.0
            )


def test_login_cli_does_not_require_api_key(
    creds_file: Path,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from together.lib.cli.auth import StoredCredentials

    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)

    def fake_login(_self: TogetherAuth, _issuer: str, **_kwargs: Any) -> StoredCredentials:
        return StoredCredentials(access_token="cli-jwt")

    monkeypatch.setattr(TogetherAuth, "login", fake_login)

    result = cli_runner.invoke(["login", "--no-browser"])
    assert result.exit_code == 0, result.output
    assert "Not logged in" not in result.output
    assert "Logged in" in result.output
    assert str(creds_file) not in result.output
    assert "tg projects list" in result.output
    assert "tg switch <project-id>" in result.output

    debug = cli_runner.invoke(["login", "--no-browser", "--debug"])
    assert debug.exit_code == 0, debug.output
    assert str(creds_file) not in debug.out_out
    assert str(creds_file) in debug.err_out


def _project_page(*ids: str) -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {
                "id": project_id,
                "name": project_id,
                "organization_id": "org-1",
                "organization_name": "Acme",
                "slug": project_id,
            }
            for project_id in ids
        ],
        "next_cursor": None,
    }


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_login_switches_when_there_is_one_project(
    respx_mock: MockRouter, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    switched: list[str] = []
    # No key yet: the client is built with a placeholder, then login installs the token.
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    def fake_login(_self: TogetherAuth, _issuer: str, **_kwargs: Any) -> StoredCredentials:
        return StoredCredentials(access_token="cli-jwt")

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr(TogetherAuth, "login", fake_login)
    monkeypatch.setattr(TogetherAuth, "switch", switch)
    respx_mock.get("/projects").mock(return_value=httpx.Response(200, json=_project_page("proj")))

    result = cli_runner.invoke(["login", "--no-browser"])
    assert result.exit_code == 0, result.output
    assert "Not logged in" not in result.output
    assert "Switched to project" in result.output
    assert "proj" in result.output
    assert "tg projects list" not in result.output
    assert switched == ["proj"]


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_login_json_reports_the_only_project(
    respx_mock: MockRouter, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_login(_self: TogetherAuth, _issuer: str, **_kwargs: Any) -> StoredCredentials:
        return StoredCredentials(access_token="cli-jwt")

    def switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        return StoredCredentials(access_token="project-jwt", project_id=project_id)

    monkeypatch.setattr(TogetherAuth, "login", fake_login)
    monkeypatch.setattr(TogetherAuth, "switch", switch)
    respx_mock.get("/projects").mock(return_value=httpx.Response(200, json=_project_page("proj")))

    result = cli_runner.invoke(["login", "--no-browser", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project_id"] == "proj"
    assert "next" not in payload


def test_login_json_includes_project_hint(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    def fake_login(_self: TogetherAuth, _issuer: str, **_kwargs: Any) -> StoredCredentials:
        return StoredCredentials(access_token="cli-jwt")

    monkeypatch.setattr(TogetherAuth, "login", fake_login)
    result = cli_runner.invoke(["login", "--no-browser", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert "tg projects list" in payload["next"]
    assert "tg switch <project-id>" in payload["next"]


@pytest.mark.usefixtures("plain_cli_help")
def test_login_help_lists_command(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    names = [
        line.strip().split(":", 1)[0]
        for line in result.output.splitlines()
        if line.strip().split(":", 1)[0] in {"login", "logout", "switch", "whoami", "batches"}
    ]
    assert names == ["batches", "whoami", "login", "logout", "switch"]


def test_device_login_revokes_then_replaces_existing_credentials(creds_file: Path) -> None:
    save_stored_credentials(
        StoredCredentials(access_token="old-parent", refresh_token="old-rt", issuer="https://api.together.ai")
    )
    save_stored_credentials(
        StoredCredentials(access_token="old-child", project_id="proj_old", issuer="https://api.together.ai")
    )
    save_stored_credentials(StoredCredentials(access_token="other", name="other", issuer="https://api.together.ai"))
    revoked: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/oauth/revoke"):
            revoked.append(dict(httpx.QueryParams(request.content.decode()))["token"])
            return httpx.Response(200, content=b"")
        if path.endswith("/v1/auth/device/code"):
            return httpx.Response(200, json=_device_auth())
        if path.endswith("/v1/auth/token"):
            return httpx.Response(200, json={"access_token": "new-jwt", "token_type": "Bearer"})
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).login(
            "https://api.together.ai", on_prompt=lambda _code: None, sleep=lambda _s: None, monotonic=lambda: 0.0
        )

    # The previous login is revoked. Its project token is a child of that session, so it is not revoked alone.
    assert revoked == ["old-rt", "other"]
    store = CredentialStore.load()
    assert [entry.entry_name for entry in store.credentials] == ["default"]
    assert store.current == "default"
    assert json.loads(creds_file.read_text(encoding="utf-8"))["credentials"][0]["access_token"] == "new-jwt"


@pytest.mark.parametrize(
    ("base_url", "issuer"),
    [
        ("https://api.together.ai/v1", "https://api.together.ai"),
        ("https://api.qa.together.ai/v1/", "https://api.qa.together.ai"),
        ("https://api.together.ai", "https://api.together.ai"),
        ("http://127.0.0.1:4010", "http://127.0.0.1:4010"),
        ("https://gw.together.ai/prefix/v1", "https://gw.together.ai/prefix"),
    ],
)
def test_issuer_from_base_url(base_url: str, issuer: str) -> None:
    assert auth.issuer_from_base_url(base_url) == issuer


def test_issuer_from_base_url_rejects_relative() -> None:
    with pytest.raises(TogetherError, match="absolute"):
        auth.issuer_from_base_url("api.together.ai/v1")


def _capture_login_issuer(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    from together.lib.cli.auth import StoredCredentials

    issuers: list[str] = []

    def fake_login(_self: TogetherAuth, issuer: str, **_kwargs: Any) -> StoredCredentials:
        issuers.append(issuer)
        return StoredCredentials(access_token="cli-jwt")

    monkeypatch.setattr(TogetherAuth, "login", fake_login)
    return issuers


def test_login_uses_base_url_flag_as_issuer(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    issuers = _capture_login_issuer(monkeypatch)
    result = cli_runner.invoke(["--base-url", "https://api.qa.together.ai/v1", "login", "--no-browser"])
    assert result.exit_code == 0, result.output
    assert issuers == ["https://api.qa.together.ai"]


def test_login_uses_base_url_env_as_issuer(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    cli_runner.env["TOGETHER_BASE_URL"] = "https://api.qa.together.ai/v1"
    issuers = _capture_login_issuer(monkeypatch)
    result = cli_runner.invoke(["login", "--no-browser"])
    assert result.exit_code == 0, result.output
    assert issuers == ["https://api.qa.together.ai"]


def test_login_defaults_to_production_even_with_other_stored_credentials(
    creds_file: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    from together.lib.cli.auth import StoredCredentials, save_stored_credentials

    save_stored_credentials(StoredCredentials(access_token="qa-jwt", issuer="https://api.qa.together.ai"))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    cli_runner.env.pop("TOGETHER_BASE_URL", None)
    monkeypatch.delenv("TOGETHER_BASE_URL", raising=False)
    issuers = _capture_login_issuer(monkeypatch)
    result = cli_runner.invoke(["login", "--no-browser"])
    assert result.exit_code == 0, result.output
    assert issuers == ["https://api.together.ai"]


def test_login_has_no_issuer_option(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["login", "--help"])
    assert result.exit_code == 0, result.output
    assert "--issuer" not in result.output


def test_login_has_no_client_id_option(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["login", "--help"])
    assert result.exit_code == 0, result.output
    assert "--client-id" not in result.output


def test_stored_client_id_wins_for_existing_sessions() -> None:
    assert auth._client_id(StoredCredentials(access_token="t", client_id="app_older_session")) == "app_older_session"
    assert auth._client_id(StoredCredentials(access_token="t")) == auth.CLI_CLIENT_ID


def _prompting_login(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_login(_self: TogetherAuth, _issuer: str, *, on_prompt: Any, **_kwargs: Any) -> StoredCredentials:
        on_prompt(
            DeviceCode(
                user_code="BCDF-GHJK",
                verification_uri="https://api.together.ai/login/device",
                browser_url="https://api.together.ai/login/device?user_code=BCDF-GHJK",
            )
        )
        return StoredCredentials(access_token="cli-jwt")

    monkeypatch.setattr(TogetherAuth, "login", fake_login)


def test_login_cli_prints_code_and_opens_browser(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    _prompting_login(monkeypatch)
    opened: list[str] = []

    def fake_open(url: str) -> bool:
        opened.append(url)
        return True

    monkeypatch.setattr("webbrowser.open", fake_open)

    result = cli_runner.invoke(["login"])

    assert result.exit_code == 0, result.output
    assert "BCDF-GHJK" in result.output
    assert "https://api.together.ai/login/device" in result.output
    assert opened == ["https://api.together.ai/login/device?user_code=BCDF-GHJK"]


def test_login_cli_no_browser_does_not_open(cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch) -> None:
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    _prompting_login(monkeypatch)
    opened: list[str] = []

    def fake_open(url: str) -> bool:
        opened.append(url)
        return True

    monkeypatch.setattr("webbrowser.open", fake_open)

    result = cli_runner.invoke(["login", "--no-browser"])

    assert result.exit_code == 0, result.output
    assert "BCDF-GHJK" in result.output
    assert opened == []


def _debug_log_path(err: str) -> str:
    for line in err.splitlines():
        if "full log written to " in line:
            return line.split("full log written to ", 1)[1].strip()
    raise AssertionError(f"debug log path not printed:\n{err}")


def test_login_debug_log_file_has_full_oauth_payloads(
    tmp_path: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tempfile

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    access_jwt = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyLTEifQ.signatureTAILabcd"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/v1/auth/device/code"):
            return httpx.Response(200, json=_device_auth(), headers={"x-request-id": "req_device_1"})
        return httpx.Response(
            200,
            json={
                "access_token": access_jwt,
                "refresh_token": "tgr_v1_opaque_refresh_secret",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

    transport = httpx.MockTransport(handler)
    patch_httpx_client(monkeypatch, transport)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    cli_runner.env["TOGETHER_BASE_URL"] = "https://api.together.ai/v1"
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(tmp_path / "credentials.json")

    result = cli_runner.invoke(["login", "--no-browser", "--debug"])

    assert result.exit_code == 0, result.output
    # The terminal gets a request/response summary for each OAuth call.
    assert "POST" in result.err_out
    with open(_debug_log_path(result.err_out), encoding="utf-8") as f:
        log = f.read()

    assert "GET https://api.together.ai/.well-known/openid-configuration" in log
    assert '"device_authorization_endpoint": "https://api.together.ai/v1/auth/device/code"' in log
    assert "POST https://api.together.ai/v1/auth/device/code" in log
    assert f"client_id={auth.CLI_CLIENT_ID}" in log
    assert '"user_code": "BCDF-GHJK"' in log
    assert "req_device_1" in log
    assert "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code" in log
    assert '"token_type": "Bearer"' in log
    assert '"expires_in": 3600' in log
    # Credential values are redacted in the file; their keys stay visible.
    assert '"refresh_token": "<redacted>"' in log
    assert '"access_token": "<redacted>"' in log
    assert '"device_code": "<redacted>"' in log
    for secret in ("tgr_v1_opaque_refresh_secret", access_jwt, "signatureTAILabcd", "odc_v1_device"):
        assert secret not in log


@pytest.mark.usefixtures("creds_file")
def test_oidc_id_env_overrides_the_cli_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OIDC_ID", "app_override")
    posted: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        posted.append(dict(httpx.QueryParams(request.content.decode()))["client_id"])
        if path.endswith("/v1/auth/device/code"):
            return httpx.Response(200, json=_device_auth())
        return httpx.Response(200, json={"access_token": "jwt-access", "token_type": "Bearer"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        tokens = TogetherAuth(http_client=client).login(
            "https://api.together.ai", on_prompt=lambda _code: None, sleep=lambda _s: None, monotonic=lambda: 0.0
        )

    # Device authorization and the token poll both use the override, and it is stored for refreshes.
    assert posted == ["app_override", "app_override"]
    assert tokens.client_id == "app_override"
    stored = load_stored_credentials()
    assert stored is not None and stored.client_id == "app_override"
    assert auth._client_id(StoredCredentials(access_token="t")) == "app_override"


def test_cli_client_id_defaults_without_oidc_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OIDC_ID", raising=False)
    assert auth.cli_client_id() == auth.CLI_CLIENT_ID
    monkeypatch.setenv("OIDC_ID", "")
    assert auth.cli_client_id() == auth.CLI_CLIENT_ID
