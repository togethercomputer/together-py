from __future__ import annotations

import os
import json
from typing import Any, Sequence, cast
from pathlib import Path

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from together import TogetherError
from tests.cli.utils import CliRunner, patch_httpx_client, stored_access_token
from together.lib.cli.auth import (
    TogetherAuth,
    CredentialStore,
    StoredCredentials,
    credentials_path,
    save_stored_credentials,
)
from together.types.project import Project


def _discovery(**overrides: Any) -> dict[str, Any]:
    body = {
        "issuer": "https://ums.together.ai",
        "authorization_endpoint": "https://api.together.ai/oauth/authorize",
        "token_endpoint": "https://api.together.ai/oauth/token",
        "grant_types_supported": [
            "authorization_code",
            "urn:ietf:params:oauth:grant-type:token-exchange",
        ],
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


def test_project_switch_exchanges_parent_token(creds_file: Path) -> None:
    parent = _parent_creds()
    save_stored_credentials(parent)
    posted: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        if path.endswith("/oauth/token"):
            posted.update(dict(httpx.QueryParams(request.content.decode())))
            return httpx.Response(
                200,
                json={
                    "access_token": "project-jwt",
                    "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                    "token_type": "Bearer",
                    "expires_in": 300,
                },
            )
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        updated = TogetherAuth(http_client=client).switch("proj_abc")

    assert credentials_path() == creds_file
    assert posted["grant_type"] == "urn:ietf:params:oauth:grant-type:token-exchange"
    assert posted["subject_token"] == parent.access_token
    assert posted["subject_token_type"] == "urn:ietf:params:oauth:token-type:jwt"
    assert posted["resource"] == "proj_abc"
    assert posted["client_id"] == "together-cli"
    # The project entry is built from the exchange response only, not merged with the login.
    assert updated == StoredCredentials(
        access_token="project-jwt",
        token_type="Bearer",
        expires_at=updated.expires_at,
        issuer="https://api.together.ai",
        client_id="together-cli",
        project_id="proj_abc",
        name="proj_abc",
    )
    assert updated.expires_at is not None
    assert stored_access_token() == "project-jwt"
    login = CredentialStore.load().get("default")
    assert login is not None
    assert login.access_token == parent.access_token
    assert login.refresh_token == "refresh-1"


def test_switch_debug_log_file_has_redacted_exchange_payload(
    creds_file: Path, tmp_path: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tempfile

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    parent = _parent_creds()
    save_stored_credentials(parent)
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        return httpx.Response(
            200, json={"access_token": "project-jwt-secret", "token_type": "Bearer", "expires_in": 300}
        )

    transport = httpx.MockTransport(handler)
    patch_httpx_client(monkeypatch, transport)

    result = cli_runner.invoke(["switch", "proj_abc", "--debug"])

    assert result.exit_code == 0, result.output
    path = next(
        line.split("full log written to ", 1)[1].strip()
        for line in result.err_out.splitlines()
        if "full log written to " in line
    )
    with open(path, encoding="utf-8") as f:
        log = f.read()
    assert "POST https://api.together.ai/oauth/token" in log
    assert "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Atoken-exchange" in log
    assert "subject_token_type=urn%3Aietf%3Aparams%3Aoauth%3Atoken-type%3Ajwt" in log
    assert "resource=proj_abc" in log
    assert "client_id=together-cli" in log
    assert "subject_token=<redacted>" in log
    assert '"access_token": "<redacted>"' in log
    assert '"token_type": "Bearer"' in log
    for secret in (parent.access_token, "eyJzdWIi", "project-jwt-secret"):
        assert secret not in log


@pytest.mark.usefixtures("creds_file")
def test_project_switch_needs_a_login_entry() -> None:
    # A project entry cannot be the exchange subject; without a login entry there is nothing to use.
    save_stored_credentials(
        StoredCredentials(access_token="old-child-jwt", issuer="https://api.together.ai", project_id="proj_old")
    )
    with pytest.raises(TogetherError, match="tg login"):
        TogetherAuth().switch("proj_new")


def test_switch_cli_from_a_project_uses_the_login_token(
    creds_file: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = _parent_creds()
    save_stored_credentials(parent)
    save_stored_credentials(
        StoredCredentials(access_token="old-child-jwt", issuer=parent.issuer, project_id="proj_old")
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    posted: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        posted.update(dict(httpx.QueryParams(request.content.decode())))
        return httpx.Response(200, json={"access_token": "new-child-jwt", "token_type": "Bearer", "expires_in": 300})

    transport = httpx.MockTransport(handler)
    patch_httpx_client(monkeypatch, transport)

    result = cli_runner.invoke(["switch", "proj_new"])

    assert result.exit_code == 0, result.output
    assert posted["subject_token"] == parent.access_token
    assert posted["resource"] == "proj_new"
    store = CredentialStore.load()
    assert store.current == "proj_new"
    assert [entry.entry_name for entry in store.credentials] == ["default", "proj_old", "proj_new"]
    assert stored_access_token() == "new-child-jwt"


@pytest.mark.parametrize(
    ("status", "error", "match"),
    [
        (400, "unsupported_grant_type", "not available"),
        (400, "invalid_grant", "Could not switch"),
        (401, "invalid_client", "Login expired"),
    ],
)
@pytest.mark.usefixtures("creds_file")
def test_project_switch_maps_oauth_errors(error: str, status: int, match: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        return httpx.Response(status, json={"error": error})

    save_stored_credentials(_parent_creds())
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(TogetherError, match=match):
            TogetherAuth(http_client=client).switch("proj_abc")


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


def _logged_in(creds_file: Path, cli_runner: CliRunner) -> None:
    save_stored_credentials(
        StoredCredentials(access_token="cli-jwt", issuer="http://127.0.0.1:4010", client_id="together-cli")
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_switch_without_project_prompts(
    respx_mock: MockRouter, creds_file: Path, cli_runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    _logged_in(creds_file, cli_runner)
    switched: list[str] = []
    respx_mock.get("/v1/projects").mock(return_value=httpx.Response(200, json=_project_page("proj_a", "proj_b")))

    async def fake_select(projects: Sequence[Project], *, preferred: str | None, message: str = "") -> str | None:
        del preferred
        assert [project.id for project in projects] == ["proj_a", "proj_b"]
        assert message == "Select a project"
        return "proj_b"

    def fake_switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        switched.append(project_id)
        updated = StoredCredentials(access_token="project-jwt", project_id=project_id, issuer="http://127.0.0.1:4010")
        save_stored_credentials(updated)
        return updated

    monkeypatch.setattr("together.lib.cli._session_is_interactive", lambda: True)
    monkeypatch.setattr("together.lib.cli.api.switch.select_project", fake_select)
    monkeypatch.setattr(TogetherAuth, "switch", fake_switch)

    result = cli_runner.invoke(["switch"])

    assert result.exit_code == 0, result.output
    assert switched == ["proj_b"]
    assert "Switched to project" in result.output
    assert "proj_b" in result.output


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_switch_without_project_prints_choices(respx_mock: MockRouter, creds_file: Path, cli_runner: CliRunner) -> None:
    _logged_in(creds_file, cli_runner)
    cli_runner.env.pop("TOGETHER_PROJECT_ID", None)
    respx_mock.get("/v1/projects").mock(return_value=httpx.Response(200, json=_project_page("proj_a", "proj_b")))

    result = cli_runner.invoke(["switch"])

    assert result.exit_code == 0, result.output
    assert "proj_a" in result.output
    assert "proj_b" in result.output
    assert "Acme" in result.output
    assert "tg switch <project-id>" in result.output
    assert "Switched to project" not in result.output
    assert stored_access_token() == "cli-jwt"


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_switch_without_project_json_lists_choices(
    respx_mock: MockRouter, creds_file: Path, cli_runner: CliRunner
) -> None:
    _logged_in(creds_file, cli_runner)
    respx_mock.get("/v1/projects").mock(return_value=httpx.Response(200, json=_project_page("proj_a", "proj_b")))

    result = cli_runner.invoke(["switch", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.out_out)
    assert payload["object"] == "list"
    assert payload["next_cursor"] is None
    assert [project["id"] for project in payload["data"]] == ["proj_a", "proj_b"]
    assert stored_access_token() == "cli-jwt"


@pytest.mark.respx(base_url=os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010"))
def test_switch_lists_with_the_login_token_across_pages(
    respx_mock: MockRouter, creds_file: Path, cli_runner: CliRunner
) -> None:
    issuer = "http://127.0.0.1:4010"
    save_stored_credentials(StoredCredentials(access_token="login-jwt", issuer=issuer, client_id="together-cli"))
    save_stored_credentials(
        StoredCredentials(access_token="project-jwt", issuer=issuer, client_id="together-cli", project_id="proj_old")
    )
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    pages = [
        {**_project_page("proj_a"), "next_cursor": "page-2"},
        _project_page("proj_b"),
    ]

    def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer login-jwt"
        return httpx.Response(200, json=pages.pop(0))

    route = respx_mock.get("/v1/projects").mock(side_effect=respond)

    result = cli_runner.invoke(["switch"])

    assert result.exit_code == 0, result.output
    assert "proj_a" in result.output
    assert "proj_b" in result.output
    assert "after=page-2" in str(cast(Call, route.calls[1]).request.url)
    assert stored_access_token() == "project-jwt"


def test_switch_cli_requires_login(creds_file: Path, cli_runner: CliRunner) -> None:
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)
    result = cli_runner.invoke(["switch", "proj_abc"])
    assert result.exit_code != 0
    assert "tg login" in result.output
    missing = cli_runner.invoke(["switch"])
    assert missing.exit_code != 0
    assert "tg login" in missing.output


def test_switch_cli_saves_project_token(
    creds_file: Path,
    cli_runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    save_stored_credentials(_parent_creds())
    cli_runner.env["TOGETHER_CREDENTIALS_PATH"] = str(creds_file)
    cli_runner.env.pop("TOGETHER_API_KEY", None)

    def fake_switch(_self: TogetherAuth, project_id: str) -> StoredCredentials:
        updated = StoredCredentials(access_token="project-jwt", project_id=project_id)
        save_stored_credentials(updated)
        return updated

    monkeypatch.setattr(TogetherAuth, "switch", fake_switch)
    result = cli_runner.invoke(["switch", "proj_abc"])
    assert result.exit_code == 0, result.output
    assert "proj_abc" in result.output
    assert stored_access_token() == "project-jwt"


def test_switch_help_lists_command(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "switch" in result.output.lower()
    help_result = cli_runner.invoke(["switch", "--help"])
    assert help_result.exit_code == 0
    assert "project" in help_result.output.lower()


@pytest.mark.usefixtures("creds_file")
def test_project_switch_adds_entry_and_keeps_login() -> None:
    save_stored_credentials(_parent_creds())

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        return httpx.Response(200, json={"access_token": "project-jwt", "token_type": "Bearer"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        TogetherAuth(http_client=client).switch("proj_abc")

    store = CredentialStore.load()
    assert store.current == "proj_abc"
    assert [entry.entry_name for entry in store.credentials] == ["default", "proj_abc"]
    default = store.get("default")
    assert default is not None and default.access_token == _parent_creds().access_token
    project = store.get("proj_abc")
    assert project is not None and project.refresh_token is None


@pytest.mark.usefixtures("creds_file")
def test_project_switch_ignores_issuer_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_ISSUER", "https://api.qa.together.ai")
    hosts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery())
        return httpx.Response(200, json={"access_token": "project-jwt", "token_type": "Bearer"})

    save_stored_credentials(_parent_creds())
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        updated = TogetherAuth(http_client=client).switch("proj_abc")

    assert "api.qa.together.ai" not in hosts
    # The saved issuer must stay the one that minted the parent, or later refreshes go elsewhere.
    assert updated.issuer == _parent_creds().issuer


def test_switch_cli_has_no_issuer_or_client_id_options(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(["switch", "--help"])
    assert result.exit_code == 0, result.output
    assert "--issuer" not in result.output
    assert "--client-id" not in result.output


@pytest.mark.usefixtures("creds_file")
def test_project_switch_uses_stored_client_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOGETHER_CLIENT_ID", "env-client-should-be-ignored")
    posted: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/.well-known/openid-configuration"):
            return httpx.Response(200, json=_discovery(together_cli_client_id="advertised-client"))
        posted.update(dict(httpx.QueryParams(request.content.decode())))
        return httpx.Response(200, json={"access_token": "project-jwt", "token_type": "Bearer"})

    save_stored_credentials(_parent_creds())
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        updated = TogetherAuth(http_client=client).switch("proj_abc")

    assert posted["client_id"] == "together-cli"
    assert updated.client_id == "together-cli"
