from __future__ import annotations

from typing import Any
from pathlib import Path

import httpx
import pytest

from together import TogetherError
from tests.cli.utils import CliRunner, patch_httpx_client
from together.lib.cli.auth import (
    TogetherAuth,
    StoredCredentials,
    load_stored_credentials,
    save_stored_credentials,
)


def _discovery(**overrides: Any) -> dict[str, Any]:
    body = {
        "issuer": "https://ums.together.ai",
        "authorization_endpoint": "https://api.together.ai/oauth/authorize",
        "token_endpoint": "https://api.together.ai/oauth/token",
        "revocation_endpoint": "https://api.together.ai/oauth/revoke",
    }
    body.update(overrides)
    return body


@pytest.fixture
def creds_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "credentials.json"
    monkeypatch.setenv("TOGETHER_CREDENTIALS_PATH", str(path))
    return path


def _parent_creds() -> StoredCredentials:
    return StoredCredentials(
        access_token="eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1In0.sig",
        refresh_token="refresh-1",
        issuer="https://api.together.ai",
        client_id="together-cli",
    )


def _project_creds() -> StoredCredentials:
    return StoredCredentials(
        access_token="child-jwt",
        issuer="https://api.together.ai",
        client_id="together-cli",
        project_id="proj_abc",
    )


def _save_switched_session() -> None:
    save_stored_credentials(_parent_creds())
    save_stored_credentials(_project_creds())


def test_revoke_prefers_refresh_token() -> None:
    posted: dict[str, str] = {}
    urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if request.url.path.endswith("/oauth/revoke"):
            urls.append(str(request.url))
            posted.update(dict(httpx.QueryParams(request.content.decode())))
            return httpx.Response(200, content=b"")
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).revoke(_parent_creds(), issuer="https://api.together.ai")

    assert urls == ["https://api.together.ai/oauth/revoke"]
    assert posted["token"] == "refresh-1"
    assert posted["token_type_hint"] == "refresh_token"
    assert posted["client_id"] == "together-cli"
    assert posted["token"] != _parent_creds().access_token


def test_revoke_falls_back_to_access_token_without_refresh() -> None:
    posted: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        posted.update(dict(httpx.QueryParams(request.content.decode())))
        return httpx.Response(200, json={})

    creds = StoredCredentials(access_token="parent-jwt", issuer="https://api.together.ai", client_id="together-cli")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).revoke(creds, issuer=str(creds.issuer))

    assert posted["token"] == "parent-jwt"
    assert posted["token_type_hint"] == "access_token"


def test_revoke_falls_back_to_token_host_when_discovery_omits_endpoint() -> None:
    urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(
                200,
                json={
                    "issuer": "https://ums.together.ai",
                    "authorization_endpoint": "https://staging.together.ai/oauth/authorize",
                    "token_endpoint": "https://staging.together.ai/oauth/token",
                },
            )
        urls.append(str(request.url))
        return httpx.Response(200, content=b"")

    creds = StoredCredentials(
        access_token="jwt",
        refresh_token="refresh-1",
        issuer="https://staging.together.ai",
        client_id="together-cli",
    )
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).revoke(creds, issuer=str(creds.issuer))

    assert urls == ["https://staging.together.ai/oauth/revoke"]


def test_revoke_maps_oauth_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        return httpx.Response(400, json={"error": "invalid_client"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(TogetherError, match="invalid_client"):
            TogetherAuth(http_client=client).revoke(_parent_creds(), issuer="https://api.together.ai")


def test_logout_cli_succeeds_when_not_logged_in(creds_file: Path, cli_runner: CliRunner) -> None:
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    result = cli_runner.invoke(["logout"])
    assert result.exit_code == 0, result.output
    assert "Logged out" in result.output
    assert not creds_file.exists()


def test_logout_cli_revokes_and_clears(
    creds_file: Path,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Current entry is the project; logout revokes the login session behind it.
    _save_switched_session()
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    called: list[str] = []

    def fake_revoke(_self: TogetherAuth, credentials: StoredCredentials, **_kwargs: Any) -> None:
        # Local credentials are wiped before anything goes over the network.
        assert not creds_file.exists()
        called.append(credentials.refresh_token or "")

    monkeypatch.setattr(TogetherAuth, "revoke", fake_revoke)
    result = cli_runner.invoke(["logout"])
    assert result.exit_code == 0, result.output
    assert "Logged out" in result.output
    assert called == ["refresh-1"]
    assert not creds_file.exists()
    assert load_stored_credentials() is None

    again = cli_runner.invoke(["logout"])
    assert again.exit_code == 0, again.output
    assert "Logged out" in again.output


def test_logout_cli_clears_local_when_revoke_fails(
    creds_file: Path,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _save_switched_session()
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    def fake_revoke(_self: TogetherAuth, _credentials: StoredCredentials, **_kwargs: Any) -> None:
        raise TogetherError("token endpoint down")

    monkeypatch.setattr(TogetherAuth, "revoke", fake_revoke)
    result = cli_runner.invoke(["logout"])
    assert result.exit_code == 0, result.output
    assert "Logged out" in result.output
    assert "token endpoint down" not in result.output
    assert not creds_file.exists()


def test_logout_help_lists_command(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "logout" in result.output.lower()
    help_result = cli_runner.invoke(["logout", "--help"])
    assert help_result.exit_code == 0
    assert "logs out" in help_result.output.lower()


def test_logout_wipes_every_entry_and_revokes_each_login(
    creds_file: Path,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    other = StoredCredentials(
        access_token="other-jwt", refresh_token="refresh-2", issuer="https://api.qa.together.ai", name="other"
    )
    save_stored_credentials(other)
    _save_switched_session()
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    revoked: list[tuple[str, str]] = []

    def fake_revoke(_self: TogetherAuth, credentials: StoredCredentials, *, issuer: str) -> None:
        revoked.append((credentials.entry_name, issuer))

    monkeypatch.setattr(TogetherAuth, "revoke", fake_revoke)

    result = cli_runner.invoke(["logout"])
    assert result.exit_code == 0, result.output
    assert not creds_file.exists()
    # The project entry is covered by revoking its login session.
    assert revoked == [("other", "https://api.qa.together.ai"), ("default", "https://api.together.ai")]


def _discovery_recorder(hosts: list[str]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(f"{request.method} {request.url}")
        if request.url.path.endswith("/.well-known/openid-configuration"):
            origin = f"{request.url.scheme}://{request.url.host}"
            return httpx.Response(
                200,
                json={
                    "issuer": origin,
                    "authorization_endpoint": f"{origin}/oauth/authorize",
                    "token_endpoint": f"{origin}/oauth/token",
                    "revocation_endpoint": f"{origin}/oauth/revoke",
                },
            )
        return httpx.Response(200, content=b"")

    return httpx.MockTransport(handler)


def test_logout_discovers_at_the_current_entry_issuer(
    creds_file: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TOGETHER_ISSUER", "https://api.together.ai")
    save_stored_credentials(
        StoredCredentials(
            access_token="qa-jwt",
            refresh_token="qa-refresh",
            issuer="https://api.qa.together.ai/",
            client_id="together-cli",
        )
    )
    save_stored_credentials(
        StoredCredentials(
            access_token="qa-child",
            issuer="https://api.qa.together.ai/",
            client_id="together-cli",
            project_id="proj_qa",
        )
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    calls: list[str] = []
    transport = _discovery_recorder(calls)
    patch_httpx_client(monkeypatch, transport)

    result = cli_runner.invoke(["logout"])

    assert result.exit_code == 0, result.output
    assert calls == [
        "GET https://api.qa.together.ai/.well-known/openid-configuration",
        "POST https://api.qa.together.ai/oauth/revoke",
    ]
    assert not creds_file.exists()


def test_logout_revokes_a_project_entry_without_a_login_on_its_own(
    creds_file: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    save_stored_credentials(
        StoredCredentials(access_token="prod-jwt", refresh_token="prod-refresh", issuer="https://api.together.ai")
    )
    save_stored_credentials(
        StoredCredentials(access_token="qa-child", issuer="https://api.qa.together.ai", project_id="proj_qa")
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    revoked: list[tuple[str, str]] = []

    def fake_revoke(_self: TogetherAuth, credentials: StoredCredentials, *, issuer: str) -> None:
        revoked.append((credentials.access_token, issuer))

    monkeypatch.setattr(TogetherAuth, "revoke", fake_revoke)
    result = cli_runner.invoke(["logout"])

    assert result.exit_code == 0, result.output
    # Each token goes only to its own issuer; the QA project has no QA login to revoke through.
    assert revoked == [("prod-jwt", "https://api.together.ai"), ("qa-child", "https://api.qa.together.ai")]
    assert not creds_file.exists()


def test_logout_without_stored_issuer_still_clears_local_credentials(creds_file: Path, cli_runner: CliRunner) -> None:
    save_stored_credentials(StoredCredentials(access_token="jwt", refresh_token="rt"))
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    result = cli_runner.invoke(["logout"])

    assert result.exit_code == 0, result.output
    assert "Logged out" in result.output
    assert not creds_file.exists()


def test_logout_cli_has_no_client_id_option(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["logout", "--help"])
    assert result.exit_code == 0, result.output
    assert "--client-id" not in result.output


def test_revoke_uses_stored_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_CLIENT_ID", "env-client-should-be-ignored")
    posted: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery(together_cli_client_id="advertised-client"))
        posted.update(dict(httpx.QueryParams(request.content.decode())))
        return httpx.Response(200, content=b"")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).revoke(_parent_creds(), issuer="https://api.together.ai")

    assert posted["client_id"] == "together-cli"
